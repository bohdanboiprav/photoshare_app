"""Init

Revision ID: d75879e1b356
Revises: 3a30dc20d94e
Create Date: 2024-01-15 01:10:17.093872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd75879e1b356'
down_revision: Union[str, None] = '3a30dc20d94e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tags_to_posts', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('tags_to_posts', 'tag_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('tags_to_posts', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tags_to_posts', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.alter_column('tags_to_posts', 'tag_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('tags_to_posts', 'post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
