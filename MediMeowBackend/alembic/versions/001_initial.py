"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 这个文件是示例，实际使用时应该通过 alembic revision --autogenerate 自动生成
    pass


def downgrade():
    pass
