"""Add okveds table

Revision ID: 350a08257aac
Revises: 02aa9ad6b427
Create Date: 2023-08-18 15:30:00.225851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '350a08257aac'
down_revision = '02aa9ad6b427'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'okveds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('okveds')
