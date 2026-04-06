# Redis And WebSocket Flow

## 1. Mục tiêu của Redis trong dự án

Redis đang được dùng cho 3 nhóm chức năng chính:

1. Cache response cho một số HTTP API chat.
2. Lưu trạng thái online tạm thời của user qua key có TTL.
3. Làm Pub/Sub broker để fan-out message WebSocket theo từng chat.

Redis không phải nơi lưu message chính. Dữ liệu message, chat, read status vẫn nằm trong MySQL qua SQLAlchemy.

## 2. Khởi tạo Redis

Redis client được tạo tại `app/db/session.py` bằng `aioredis.ConnectionPool`.

- Pool dùng các biến cấu hình `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_DB`.
- `decode_responses=True` nên dữ liệu string đọc từ Redis sẽ ở dạng `str`, không phải `bytes`.

Luồng startup/shutdown:

- `app/main.py`
  - Khi startup: tạo `app.state.redis` và gọi `ping()` để kiểm tra Redis.
  - Nếu Redis lỗi: app vẫn chạy nhưng `app.state.redis = None`.
  - Khi shutdown: đóng client Redis và disconnect pool.

Dependency dùng chung:

- `app/dependencies.py`
  - `get_cache()` lấy Redis client từ `app.state.redis`.
  - Nếu chưa có thì tạo mới từ `get_redis_client()`.
  - `get_cache_setting()` trả về cờ `CACHE_ENABLED`.

## 3. Cấu trúc key Redis hiện tại

### 3.1. Cache HTTP

`GET /api/v1/chat/{chat_guid}/messages`

- Key: `messages_v2_{chat_guid}_{current_user_id}_{size}`
- Giá trị: JSON string của `GetMessagesSchema`
- Lý do có `current_user_id`:
  - response phụ thuộc `is_read`
  - response phụ thuộc `last_read_message`
- Lý do có `v2`:
  - tránh dùng lại cache cũ khi đổi schema response

`GET /api/v1/chat/chats/direct`

- Key: `direct_chats_{current_user['id']}`
- Giá trị: JSON string của `GetDirectChatsSchema`

### 3.2. Online presence

- Key: `user:{user_id}:status`
- Giá trị: `"online"`
- TTL: `60` giây

Key này được refresh lại mỗi khi:

- user vừa connect WebSocket
- user gửi `new_message`
- user gửi `message_read`
- user gửi `user_typing`
- user nhận event `add_user_to_chat`

### 3.3. Pub/Sub channel

- Channel name chính là `chat_guid`
- Message publish lên channel là JSON string hoặc dict được serialize sang JSON

## 4. Cache HTTP hoạt động như thế nào

### 4.1. API lấy messages

File chính: `app/api/v1/chat.py`

Luồng:

1. API nhận `chat_guid` và `size`.
2. Load chat từ DB.
3. Tính `unread_messages_count`.
4. Lấy `size = max(size, unread_messages_count)`.
5. Tạo cache key `messages_v2_{chat_guid}_{current_user_id}_{size}`.
6. Nếu `CACHE_ENABLED` và Redis có key:
   trả về thẳng `json.loads(cached_chat_messages)`.
7. Nếu cache miss:
   gọi `get_chat_messages()` trong `app/services/chat/chat_service.py`.
8. Build `GetMessagesSchema`.
9. Ghi JSON vào Redis với TTL `settings.REDIS_CACHE_EXPIRATION_SECONDS`.

### 4.2. API lấy danh sách direct chats

Luồng:

1. Tạo key `direct_chats_{current_user['id']}`.
2. Nếu cache hit thì trả về luôn.
3. Nếu miss:
   - load danh sách chat từ DB
   - tính `new_messages_count` cho từng chat
   - tính `total_unread_messages_count`
4. Serialize response vào Redis.

### 4.3. Xóa cache

File: `app/utils/cache_utils.py`

Các helper hiện có:

- `clear_cache_for_get_messages(cache, chat_guid)`
  - xóa theo pattern `messages*_{chat_guid}_*`
  - match được cả key cũ và key mới
- `clear_cache_for_get_direct_chats(cache, user)`
  - xóa key `direct_chats_{user.guid}`
- `clear_cache_for_all_users(cache)`
  - xóa pattern `*all_users`

Lưu ý:

- `direct_chats_{current_user['id']}` đang dùng `id`
- `clear_cache_for_get_direct_chats()` đang xóa theo `user.guid`

Điều này tạo ra lệch key format và có thể khiến cache direct chats không bị xóa đúng trong một số trường hợp. Đây là điểm nên sửa tiếp.

## 5. Kiến trúc WebSocket

File entrypoint: `app/services/websocket/router.py`

Endpoint:

- `ws://<host>/api/v1/ws/?token=<jwt>`
- hoặc truyền `Authorization: Bearer <token>`

### 5.1. Xác thực WebSocket

Hàm `get_current_ws_user()`:

1. Lấy token từ header hoặc query param.
2. Decode JWT bằng `JWT_SECRET_KEY` và `ALGORITHM`.
3. Lấy `id` từ payload.
4. Query DB để bảo đảm user còn `active=True` và `deleted=False`.
5. Nếu fail thì đóng socket với code `1008`.

### 5.2. Khi một socket kết nối

Trong `websocket_endpoint()`:

1. Xác thực user.
2. `socket_manager.connect_socket()` gọi `websocket.accept()`.
3. Thêm socket vào map `user_guid_to_websocket`.
4. Gọi `mark_user_as_online()` để tạo key presence trong Redis.
5. Lấy tất cả direct chats đang hoạt động của user.
6. Với mỗi chat:
   gọi `socket_manager.add_user_to_chat(chat_guid, websocket)`.
7. Tạo background task `check_user_statuses(...)`.
8. Bắt đầu vòng lặp nhận message JSON từ client.

### 5.3. WebSocketManager quản lý gì

File: `app/managers/websocket_manager.py`

Manager giữ 3 thành phần:

- `handlers`
  - map từ `message_type` sang async handler
- `chats`
  - dạng `{chat_guid: {ws1, ws2, ...}}`
  - dùng để biết socket nào đang theo dõi chat nào
- `user_guid_to_websocket`
  - dạng `{user_guid: {ws1, ws2, ...}}`
  - dùng khi cần push event trực tiếp tới toàn bộ socket của một user

### 5.4. Pub/Sub hoạt động ra sao

File: `app/managers/pubsub_manager.py`

Khi socket đầu tiên join một chat:

1. `WebSocketManager.add_user_to_chat()` tạo set socket cho `chat_guid`.
2. Gọi `pubsub_client.connect()`.
3. Subscribe vào Redis channel có tên bằng `chat_guid`.
4. Tạo task `_pubsub_data_reader(pubsub_subscriber)`.

Khi broadcast:

1. `broadcast_to_chat(chat_guid, message)` publish message lên Redis channel `chat_guid`.
2. `_pubsub_data_reader()` đọc message từ Redis Pub/Sub.
3. Lấy danh sách socket trong `self.chats[chat_guid]`.
4. Gửi message tới từng socket bằng `send_text()`.

Ý nghĩa:

- Redis đóng vai trò broker trung gian.
- WebSocket handler không gửi trực tiếp cho từng socket trong chat.
- Cách này dễ mở rộng hơn khi có nhiều nơi cùng publish message.

## 6. Luồng xử lý từng loại message WebSocket

File handler: `app/services/websocket/handlers.py`

### 6.1. `new_message`

Client gửi:

```json
{
  "type": "new_message",
  "chat_guid": "...",
  "user_guid": "...",
  "content": "..."
}
```

Luồng:

1. Validate payload bằng `ReceiveMessageSchema`.
2. Nếu chat chưa có trong `chats` local của socket:
   - tra `chat_id` từ DB
   - add socket vào chat
   - đánh dấu cần notify friend về chat mới
3. Tạo `Message` mới trong DB.
4. Cập nhật `chat.updated`.
5. Commit transaction.
6. Refresh `message.user`, `message.chat`, `chat.user`.
7. Refresh presence bằng `mark_user_as_online()`.
8. Nếu cache bật:
   - clear cache direct chats cho các user trong chat
   - clear cache messages của chat
9. Build `SendMessageSchema`.
10. Publish message vào Redis channel của chat.
11. Nếu đây là chat mới:
    gửi thêm event `new_chat_created` tới socket của friend.

### 6.2. `message_read`

Client gửi:

```json
{
  "type": "message_read",
  "chat_guid": "...",
  "message_guid": "..."
}
```

Luồng:

1. Validate bằng `MessageReadSchema`.
2. Load message từ DB.
3. Kiểm tra chat có nằm trong `chats` local không.
4. Gọi `mark_last_read_message()`.
5. Nếu read status thay đổi:
   - refresh presence
   - clear cache messages của chat
   - broadcast event:

```json
{
  "type": "message_read",
  "user_guid": "...",
  "chat_guid": "...",
  "last_read_message_guid": "...",
  "last_read_message_created_at": "..."
}
```

### 6.3. `user_typing`

Client gửi:

```json
{
  "type": "user_typing",
  "chat_guid": "...",
  "user_guid": "..."
}
```

Luồng:

1. Validate payload.
2. Kiểm tra chat có trong `chats` local không.
3. Refresh presence.
4. Broadcast lại payload cho các socket trong chat.

### 6.4. `add_user_to_chat`

Đây là event nội bộ để socket của user còn lại join một chat mới mà không cần refresh danh sách chat.

Luồng:

1. Validate payload.
2. Add socket vào `socket_manager.chats[chat_guid]`.
3. Ghi `chat_guid -> chat_id` vào biến `chats` local của websocket endpoint.
4. Refresh presence.

### 6.5. `chat_deleted`

Event này dùng để notify các socket khác trong cùng chat rằng chat đã bị xóa.

Handler:

1. Validate payload.
2. Kiểm tra chat có trong `chats` local không.
3. Lấy toàn bộ socket đang gắn với `chat_guid`.
4. Gửi trực tiếp JSON `chat_deleted` tới các socket khác, trừ socket vừa gửi.

Khác với các message còn lại:

- `chat_deleted` đang gửi trực tiếp bằng `socket.send_json(...)`
- không publish qua Redis Pub/Sub

## 7. Background task kiểm tra trạng thái user

File: `app/services/websocket/services.py`

Hàm `check_user_statuses()` chạy vòng lặp vô hạn:

1. Kiểm tra key `user:{user_id}:status` có còn tồn tại trong Redis hay không.
2. Lấy giao của:
   - các chat socket đang theo dõi
   - các chat thuộc `current_user.chat`
3. Nếu key còn tồn tại:
   broadcast status `online`
4. Nếu key hết hạn:
   broadcast status `inactive`
5. Sleep `settings.SECONDS_TO_SEND_USER_STATUS`

Ngoài ra:

- `mark_user_as_offline()` xóa key Redis và broadcast `offline`
- hàm này được gọi khi socket disconnect

## 8. Luồng disconnect WebSocket

Khi `WebSocketDisconnect`:

1. Remove socket khỏi từng chat trong `socket_manager.chats`.
2. Với mỗi chat, gọi `mark_user_as_offline()`.
3. Nếu chat không còn socket nào, unsubscribe Redis channel tương ứng.
4. Disconnect Pub/Sub client.
5. Cancel background task `user_status_task`.
6. Remove socket khỏi `user_guid_to_websocket`.

## 9. Tương tác giữa HTTP cache và WebSocket

Điểm quan trọng của thiết kế hiện tại:

- HTTP API phục vụ dữ liệu ban đầu và lịch sử chat.
- WebSocket phục vụ cập nhật realtime.
- Mỗi khi realtime làm dữ liệu thay đổi, handler sẽ clear cache HTTP liên quan.

Ví dụ:

- gửi message mới
  - invalidate `messages*_{chat_guid}_*`
  - invalidate danh sách direct chats
- mark read
  - invalidate `messages*_{chat_guid}_*`

Nhờ vậy:

- API không trả dữ liệu cũ quá lâu
- frontend có thể vừa dùng HTTP để load ban đầu, vừa dùng WebSocket để cập nhật realtime

## 10. Những điểm cần lưu ý trong implementation hiện tại

### 10.1. Lệch key direct chats

`get_user_chats_view()` cache theo:

- `direct_chats_{current_user['id']}`

Nhưng `clear_cache_for_get_direct_chats()` xóa theo:

- `direct_chats_{user.guid}`

Hai format này không giống nhau. Nếu muốn invalidation đúng, nên thống nhất chỉ dùng `id` hoặc chỉ dùng `guid`.

### 10.2. TTL presence không khớp comment

Trong `mark_user_as_online()`:

- code dùng `ex=60`
- comment ghi `1 hours`

Comment này sai với implementation thực tế.

### 10.3. `chat_deleted` không đi qua Redis Pub/Sub

Điều này không sai nếu app chỉ có một process, nhưng nếu scale nhiều instance thì event `chat_deleted` sẽ không tự fan-out liên tiến trình giống `new_message`.

### 10.4. Pub/Sub client đang là state dùng chung trong `WebSocketManager`

`socket_manager` là singleton import-level.
`pubsub_client` cũng là object dùng chung.

Điều này hoạt động được trong mô hình hiện tại, nhưng khi số socket lớn hoặc nhiều subscribe/unsubscribe diễn ra đồng thời, cần review kỹ lại vòng đời kết nối Pub/Sub.

### 10.5. `message_read` không invalidate direct chats

Hiện tại `message_read` chỉ xóa cache messages. Nếu UI direct chats phụ thuộc unread count theo read status thời gian thực, có thể cần invalidate thêm cache danh sách direct chats.

## 11. Tóm tắt ngắn

- MySQL lưu dữ liệu gốc: chat, message, read status.
- Redis cache một phần HTTP response.
- Redis cũng giữ presence bằng key có TTL.
- Redis Pub/Sub làm lớp fan-out cho WebSocket theo `chat_guid`.
- `websocket_endpoint()` là nơi xác thực, join chat, nhận payload và dispatch tới handler.
- `handlers.py` là nơi xử lý nghiệp vụ realtime.
- Khi realtime làm dữ liệu đổi trạng thái, cache HTTP liên quan sẽ bị xóa để tránh stale data.
