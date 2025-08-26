from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20ac8a442bb7'
down_revision = '35aec7555393'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'equipment_classification_report_selection',
        
        sa.Column('medical_id', sa.Integer,
            primary_key=True, 
            
            nullable=False, 
            
        ),
        
        sa.Column('rank', sa.Integer,
            primary_key=True, 
            
            nullable=False, 
            
        ),
        
        sa.Column('classification_id', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('reg_user_id', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('regdate', sa.DateTime,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('update_user_id', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('lastupdate', sa.DateTime,
            
            
            nullable=False, 
            
        ),
        
    )

def downgrade():
    op.drop_table('equipment_classification_report_selection')