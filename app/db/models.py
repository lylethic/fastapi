from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import CHAR, Column, DECIMAL, DateTime, Enum, ForeignKeyConstraint, Index, Integer, JSON, String, Table, Text, text
from sqlalchemy.dialects.mysql import ENUM, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AffiliateCampaignParticipantsStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    BLOCKED = 'blocked'


class AffiliateCampaignsAttributionModel(str, enum.Enum):
    LAST_CLICK = 'last_click'
    FIRST_CLICK = 'first_click'


class AffiliateCampaignsCampaignType(str, enum.Enum):
    CPS = 'cps'
    CPL = 'cpl'
    CPA = 'cpa'
    REVSHARE = 'revshare'
    HYBRID = 'hybrid'


class AffiliateCampaignsStatus(str, enum.Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    PAUSED = 'paused'
    CLOSED = 'closed'


class AffiliateCommissionsCommissionType(str, enum.Enum):
    FIXED = 'fixed'
    PERCENTAGE = 'percentage'
    REVSHARE = 'revshare'
    BONUS = 'bonus'


class AffiliateCommissionsStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    PAID = 'paid'
    REJECTED = 'rejected'


class AffiliateConversionsConversionType(str, enum.Enum):
    LEAD = 'lead'
    ACTION = 'action'
    SALE = 'sale'
    INSTALL = 'install'
    REGISTER = 'register'


class AffiliateConversionsStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'


class AffiliatePayoutRequestsPaymentMethod(str, enum.Enum):
    BANK_TRANSFER = 'bank_transfer'
    EWALLET = 'ewallet'
    PAYPAL = 'paypal'


class AffiliatePayoutRequestsStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    PAID = 'paid'
    REJECTED = 'rejected'


class AffiliateProfilesAffiliateLevel(str, enum.Enum):
    F0 = 'F0'
    F1 = 'F1'
    F2 = 'F2'


class AffiliateProfilesPaymentMethod(str, enum.Enum):
    BANK_TRANSFER = 'bank_transfer'
    EWALLET = 'ewallet'
    PAYPAL = 'paypal'


class AffiliateProfilesStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'


class ChatChatType(str, enum.Enum):
    DIRECT = 'direct'
    GROUP = 'group'


class MessageMessageType(str, enum.Enum):
    TEXT = 'text'
    FILE = 'file'


class Chat(Base):
    __tablename__ = 'chat'
    __table_args__ = (
        Index('idx_chat_on_guid', 'guid'),
        Index('idx_chat_on_is_deleted_chat_type', 'deleted', 'chat_type'),
        Index('uq_chat_guid', 'guid', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    guid: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    chat_type: Mapped[ChatChatType] = mapped_column(Enum(ChatChatType, values_callable=lambda cls: [member.value for member in cls]), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    user: Mapped[list['Users']] = relationship('Users', secondary='chat_participant', back_populates='chat')
    message: Mapped[list['Message']] = relationship('Message', back_populates='chat')
    read_status: Mapped[list['ReadStatus']] = relationship('ReadStatus', back_populates='chat')


class Permissions(Base):
    __tablename__ = 'permissions'

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    name: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    role_permissions: Mapped[list['RolePermissions']] = relationship('RolePermissions', back_populates='permission')


class Roles(Base):
    __tablename__ = 'roles'

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    name: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    role_permissions: Mapped[list['RolePermissions']] = relationship('RolePermissions', back_populates='role')
    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='role')


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    email: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    password: Mapped[str] = mapped_column(String(500, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    is_send_email: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    username: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    profile_pic: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    city: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    last_login_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    token: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    guid: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    chat: Mapped[list['Chat']] = relationship('Chat', secondary='chat_participant', back_populates='user')
    affiliate_profiles: Mapped[list['AffiliateProfiles']] = relationship('AffiliateProfiles', back_populates='user')
    merchant_profiles: Mapped[list['MerchantProfiles']] = relationship('MerchantProfiles', back_populates='user')
    message: Mapped[list['Message']] = relationship('Message', back_populates='user')
    read_status: Mapped[list['ReadStatus']] = relationship('ReadStatus', back_populates='user')
    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='user')


class AffiliateProfiles(Base):
    __tablename__ = 'affiliate_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_affiliate_profiles_user'),
        Index('idx_affiliate_profiles_status', 'status'),
        Index('uq_affiliate_profiles_code', 'affiliate_code', unique=True),
        Index('uq_affiliate_profiles_user_id', 'user_id', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    affiliate_code: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False)
    status: Mapped[AffiliateProfilesStatus] = mapped_column(Enum(AffiliateProfilesStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'pending'"))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    affiliate_level: Mapped[AffiliateProfilesAffiliateLevel] = mapped_column(Enum(AffiliateProfilesAffiliateLevel, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'F2'"))
    display_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    traffic_source: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    social_channel: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    payment_method: Mapped[Optional[AffiliateProfilesPaymentMethod]] = mapped_column(Enum(AffiliateProfilesPaymentMethod, values_callable=lambda cls: [member.value for member in cls]))
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    bank_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    tax_number: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    parent_affiliate_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    user: Mapped['Users'] = relationship('Users', back_populates='affiliate_profiles')
    affiliate_payout_requests: Mapped[list['AffiliatePayoutRequests']] = relationship('AffiliatePayoutRequests', back_populates='affiliate')
    affiliate_campaign_participants: Mapped[list['AffiliateCampaignParticipants']] = relationship('AffiliateCampaignParticipants', back_populates='affiliate')
    affiliate_links: Mapped[list['AffiliateLinks']] = relationship('AffiliateLinks', back_populates='affiliate')
    affiliate_clicks: Mapped[list['AffiliateClicks']] = relationship('AffiliateClicks', back_populates='affiliate')
    affiliate_conversions: Mapped[list['AffiliateConversions']] = relationship('AffiliateConversions', back_populates='affiliate')
    affiliate_commissions: Mapped[list['AffiliateCommissions']] = relationship('AffiliateCommissions', back_populates='affiliate')


t_chat_participant = Table(
    'chat_participant', Base.metadata,
    Column('user_id', CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True),
    Column('chat_id', CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True),
    ForeignKeyConstraint(['chat_id'], ['chat.id'], ondelete='CASCADE', name='fk_chat_participant_chat'),
    ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_chat_participant_user'),
    Index('fk_chat_participant_chat', 'chat_id')
)


class MerchantProfiles(Base):
    __tablename__ = 'merchant_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_merchant_profiles_user'),
        Index('uq_merchant_profiles_tax_code', 'tax_code', unique=True),
        Index('uq_merchant_profiles_user_id', 'user_id', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    website: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb4_unicode_ci'))
    contact_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    tax_code: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    business_type: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    billing_email: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    address: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    user: Mapped['Users'] = relationship('Users', back_populates='merchant_profiles')
    affiliate_campaigns: Mapped[list['AffiliateCampaigns']] = relationship('AffiliateCampaigns', back_populates='merchant')


class Message(Base):
    __tablename__ = 'message'
    __table_args__ = (
        ForeignKeyConstraint(['chat_id'], ['chat.id'], ondelete='CASCADE', name='fk_message_chat'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_message_user'),
        Index('idx_message_on_chat_id', 'chat_id'),
        Index('idx_message_on_user_id', 'user_id'),
        Index('idx_message_on_user_id_chat_id', 'chat_id', 'user_id'),
        Index('uq_message_guid', 'guid', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    guid: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    message_type: Mapped[MessageMessageType] = mapped_column(Enum(MessageMessageType, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'text'"))
    content: Mapped[str] = mapped_column(String(5000, 'utf8mb4_unicode_ci'), nullable=False)
    user_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    chat_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    file_name: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    file_path: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    chat: Mapped['Chat'] = relationship('Chat', back_populates='message')
    user: Mapped['Users'] = relationship('Users', back_populates='message')


class ReadStatus(Base):
    __tablename__ = 'read_status'
    __table_args__ = (
        ForeignKeyConstraint(['chat_id'], ['chat.id'], ondelete='CASCADE', name='fk_read_status_chat'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_read_status_user'),
        Index('idx_read_status_on_chat_id', 'chat_id'),
        Index('idx_read_status_on_user_id', 'user_id')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    chat_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    last_read_message_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    chat: Mapped['Chat'] = relationship('Chat', back_populates='read_status')
    user: Mapped['Users'] = relationship('Users', back_populates='read_status')


class RolePermissions(Base):
    __tablename__ = 'role_permissions'
    __table_args__ = (
        ForeignKeyConstraint(['permission_id'], ['permissions.id'], name='role_permissions_ibfk_2'),
        ForeignKeyConstraint(['role_id'], ['roles.id'], name='role_permissions_ibfk_1'),
        Index('permission_id', 'permission_id')
    )

    role_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    permission_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    permission: Mapped['Permissions'] = relationship('Permissions', back_populates='role_permissions')
    role: Mapped['Roles'] = relationship('Roles', back_populates='role_permissions')


class UserRoles(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.id'], name='user_roles_ibfk_2'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_roles_ibfk_1'),
        Index('role_id', 'role_id')
    )

    user_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    role_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    role: Mapped['Roles'] = relationship('Roles', back_populates='user_roles')
    user: Mapped['Users'] = relationship('Users', back_populates='user_roles')


class AffiliateCampaigns(Base):
    __tablename__ = 'affiliate_campaigns'
    __table_args__ = (
        ForeignKeyConstraint(['merchant_id'], ['merchant_profiles.id'], name='fk_affiliate_campaigns_merchant'),
        Index('idx_affiliate_campaigns_merchant_id', 'merchant_id'),
        Index('idx_affiliate_campaigns_status', 'status')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    name: Mapped[str] = mapped_column(String(255, 'utf8mb4_unicode_ci'), nullable=False)
    campaign_type: Mapped[AffiliateCampaignsCampaignType] = mapped_column(Enum(AffiliateCampaignsCampaignType, values_callable=lambda cls: [member.value for member in cls]), nullable=False)
    commission_value: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    cookie_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("'30'"))
    attribution_model: Mapped[AffiliateCampaignsAttributionModel] = mapped_column(Enum(AffiliateCampaignsAttributionModel, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'last_click'"))
    status: Mapped[AffiliateCampaignsStatus] = mapped_column(Enum(AffiliateCampaignsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'draft'"))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    description: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    landing_page_url: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    commission_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 4))
    start_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    terms_conditions: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    merchant: Mapped['MerchantProfiles'] = relationship('MerchantProfiles', back_populates='affiliate_campaigns')
    affiliate_campaign_participants: Mapped[list['AffiliateCampaignParticipants']] = relationship('AffiliateCampaignParticipants', back_populates='campaign')
    affiliate_links: Mapped[list['AffiliateLinks']] = relationship('AffiliateLinks', back_populates='campaign')
    affiliate_clicks: Mapped[list['AffiliateClicks']] = relationship('AffiliateClicks', back_populates='campaign')
    affiliate_conversions: Mapped[list['AffiliateConversions']] = relationship('AffiliateConversions', back_populates='campaign')
    affiliate_commissions: Mapped[list['AffiliateCommissions']] = relationship('AffiliateCommissions', back_populates='campaign')


class AffiliatePayoutRequests(Base):
    __tablename__ = 'affiliate_payout_requests'
    __table_args__ = (
        ForeignKeyConstraint(['affiliate_id'], ['affiliate_profiles.id'], name='fk_affiliate_payout_requests_affiliate'),
        Index('idx_affiliate_payout_requests_affiliate_id', 'affiliate_id'),
        Index('idx_affiliate_payout_requests_status', 'status'),
        Index('uq_affiliate_payout_requests_code', 'request_code', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    affiliate_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    request_code: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    payment_method: Mapped[AffiliatePayoutRequestsPaymentMethod] = mapped_column(Enum(AffiliatePayoutRequestsPaymentMethod, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'bank_transfer'"))
    status: Mapped[AffiliatePayoutRequestsStatus] = mapped_column(Enum(AffiliatePayoutRequestsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'pending'"))
    requested_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    bank_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    rejected_reason: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    affiliate: Mapped['AffiliateProfiles'] = relationship('AffiliateProfiles', back_populates='affiliate_payout_requests')
    affiliate_payout_items: Mapped[list['AffiliatePayoutItems']] = relationship('AffiliatePayoutItems', back_populates='payout_request')


class AffiliateCampaignParticipants(Base):
    __tablename__ = 'affiliate_campaign_participants'
    __table_args__ = (
        ForeignKeyConstraint(['affiliate_id'], ['affiliate_profiles.id'], name='fk_campaign_participants_affiliate'),
        ForeignKeyConstraint(['campaign_id'], ['affiliate_campaigns.id'], name='fk_campaign_participants_campaign'),
        Index('idx_campaign_participants_affiliate_id', 'affiliate_id'),
        Index('idx_campaign_participants_status', 'status')
    )

    campaign_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    affiliate_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    status: Mapped[AffiliateCampaignParticipantsStatus] = mapped_column(Enum(AffiliateCampaignParticipantsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'pending'"))
    joined_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    note: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    affiliate: Mapped['AffiliateProfiles'] = relationship('AffiliateProfiles', back_populates='affiliate_campaign_participants')
    campaign: Mapped['AffiliateCampaigns'] = relationship('AffiliateCampaigns', back_populates='affiliate_campaign_participants')


class AffiliateLinks(Base):
    __tablename__ = 'affiliate_links'
    __table_args__ = (
        ForeignKeyConstraint(['affiliate_id'], ['affiliate_profiles.id'], name='fk_affiliate_links_affiliate'),
        ForeignKeyConstraint(['campaign_id'], ['affiliate_campaigns.id'], name='fk_affiliate_links_campaign'),
        Index('fk_affiliate_links_affiliate', 'affiliate_id'),
        Index('idx_affiliate_links_campaign_affiliate', 'campaign_id', 'affiliate_id'),
        Index('uq_affiliate_links_code', 'code', unique=True),
        Index('uq_affiliate_links_guid', 'guid', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    guid: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    campaign_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    affiliate_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    code: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False)
    destination_url: Mapped[str] = mapped_column(String(1000, 'utf8mb4_unicode_ci'), nullable=False)
    tracking_url: Mapped[str] = mapped_column(String(1000, 'utf8mb4_unicode_ci'), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    short_code: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    utm_source: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    affiliate: Mapped['AffiliateProfiles'] = relationship('AffiliateProfiles', back_populates='affiliate_links')
    campaign: Mapped['AffiliateCampaigns'] = relationship('AffiliateCampaigns', back_populates='affiliate_links')
    affiliate_clicks: Mapped[list['AffiliateClicks']] = relationship('AffiliateClicks', back_populates='link')


class AffiliateClicks(Base):
    __tablename__ = 'affiliate_clicks'
    __table_args__ = (
        ForeignKeyConstraint(['affiliate_id'], ['affiliate_profiles.id'], name='fk_affiliate_clicks_affiliate'),
        ForeignKeyConstraint(['campaign_id'], ['affiliate_campaigns.id'], name='fk_affiliate_clicks_campaign'),
        ForeignKeyConstraint(['link_id'], ['affiliate_links.id'], name='fk_affiliate_clicks_link'),
        Index('fk_affiliate_clicks_link', 'link_id'),
        Index('idx_affiliate_clicks_affiliate_id', 'affiliate_id'),
        Index('idx_affiliate_clicks_campaign_id', 'campaign_id'),
        Index('idx_affiliate_clicks_created', 'created'),
        Index('idx_affiliate_clicks_session_id', 'session_id'),
        Index('uq_affiliate_clicks_click_code', 'click_code', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    affiliate_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    click_code: Mapped[str] = mapped_column(String(100, 'utf8mb4_unicode_ci'), nullable=False)
    is_suspicious: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    link_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45, 'utf8mb4_unicode_ci'))
    user_agent: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    referer_url: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    landing_url: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    session_id: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    device_type: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    os_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    browser_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    country: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    city: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    affiliate: Mapped['AffiliateProfiles'] = relationship('AffiliateProfiles', back_populates='affiliate_clicks')
    campaign: Mapped['AffiliateCampaigns'] = relationship('AffiliateCampaigns', back_populates='affiliate_clicks')
    link: Mapped[Optional['AffiliateLinks']] = relationship('AffiliateLinks', back_populates='affiliate_clicks')
    affiliate_conversions: Mapped[list['AffiliateConversions']] = relationship('AffiliateConversions', back_populates='click')


class AffiliateConversions(Base):
    __tablename__ = 'affiliate_conversions'
    __table_args__ = (
        ForeignKeyConstraint(['affiliate_id'], ['affiliate_profiles.id'], name='fk_affiliate_conversions_affiliate'),
        ForeignKeyConstraint(['campaign_id'], ['affiliate_campaigns.id'], name='fk_affiliate_conversions_campaign'),
        ForeignKeyConstraint(['click_id'], ['affiliate_clicks.id'], name='fk_affiliate_conversions_click'),
        Index('fk_affiliate_conversions_click', 'click_id'),
        Index('idx_affiliate_conversions_affiliate_id', 'affiliate_id'),
        Index('idx_affiliate_conversions_campaign_id', 'campaign_id'),
        Index('idx_affiliate_conversions_ref_order_id', 'ref_order_id'),
        Index('idx_affiliate_conversions_status', 'status')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    affiliate_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    conversion_type: Mapped[AffiliateConversionsConversionType] = mapped_column(Enum(AffiliateConversionsConversionType, values_callable=lambda cls: [member.value for member in cls]), nullable=False)
    status: Mapped[AffiliateConversionsStatus] = mapped_column(Enum(AffiliateConversionsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'pending'"))
    conversion_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    click_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    ref_order_id: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    ref_lead_id: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_unicode_ci'))
    customer_name: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    customer_email: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_unicode_ci'))
    customer_phone: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_unicode_ci'))
    order_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    commission_base: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    rejected_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    reject_reason: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    metadata_: Mapped[Optional[dict]] = mapped_column('metadata', JSON)
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    affiliate: Mapped['AffiliateProfiles'] = relationship('AffiliateProfiles', back_populates='affiliate_conversions')
    campaign: Mapped['AffiliateCampaigns'] = relationship('AffiliateCampaigns', back_populates='affiliate_conversions')
    click: Mapped[Optional['AffiliateClicks']] = relationship('AffiliateClicks', back_populates='affiliate_conversions')
    affiliate_commissions: Mapped[list['AffiliateCommissions']] = relationship('AffiliateCommissions', back_populates='conversion')


class AffiliateCommissions(Base):
    __tablename__ = 'affiliate_commissions'
    __table_args__ = (
        ForeignKeyConstraint(['affiliate_id'], ['affiliate_profiles.id'], name='fk_affiliate_commissions_affiliate'),
        ForeignKeyConstraint(['campaign_id'], ['affiliate_campaigns.id'], name='fk_affiliate_commissions_campaign'),
        ForeignKeyConstraint(['conversion_id'], ['affiliate_conversions.id'], name='fk_affiliate_commissions_conversion'),
        Index('fk_affiliate_commissions_conversion', 'conversion_id'),
        Index('idx_affiliate_commissions_affiliate_id', 'affiliate_id'),
        Index('idx_affiliate_commissions_campaign_id', 'campaign_id'),
        Index('idx_affiliate_commissions_status', 'status')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    conversion_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    campaign_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    affiliate_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), nullable=False)
    commission_type: Mapped[AffiliateCommissionsCommissionType] = mapped_column(Enum(AffiliateCommissionsCommissionType, values_callable=lambda cls: [member.value for member in cls]), nullable=False)
    commission_value: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    status: Mapped[AffiliateCommissionsStatus] = mapped_column(Enum(AffiliateCommissionsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'pending'"))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    rate_value: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 4))
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    paid_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    note: Mapped[Optional[str]] = mapped_column(String(1000, 'utf8mb4_unicode_ci'))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    affiliate: Mapped['AffiliateProfiles'] = relationship('AffiliateProfiles', back_populates='affiliate_commissions')
    campaign: Mapped['AffiliateCampaigns'] = relationship('AffiliateCampaigns', back_populates='affiliate_commissions')
    conversion: Mapped['AffiliateConversions'] = relationship('AffiliateConversions', back_populates='affiliate_commissions')
    affiliate_payout_items: Mapped[list['AffiliatePayoutItems']] = relationship('AffiliatePayoutItems', back_populates='commission')


class AffiliatePayoutItems(Base):
    __tablename__ = 'affiliate_payout_items'
    __table_args__ = (
        ForeignKeyConstraint(['commission_id'], ['affiliate_commissions.id'], name='fk_affiliate_payout_items_commission'),
        ForeignKeyConstraint(['payout_request_id'], ['affiliate_payout_requests.id'], name='fk_affiliate_payout_items_request'),
        Index('idx_affiliate_payout_items_commission_id', 'commission_id')
    )

    payout_request_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    commission_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    deleted: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    updated: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))
    updated_by: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_unicode_ci'))

    commission: Mapped['AffiliateCommissions'] = relationship('AffiliateCommissions', back_populates='affiliate_payout_items')
    payout_request: Mapped['AffiliatePayoutRequests'] = relationship('AffiliatePayoutRequests', back_populates='affiliate_payout_items')
