from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1767a534a2e0'
down_revision = '10eb1a908c44'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'medical_equipment_analysis_setting',
        
        sa.Column('ledger_id', sa.Integer,
            primary_key=True, 
            
            nullable=False, 
            
        ),
        
        sa.Column('override_is_included', sa.Boolean,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('override_classification_id', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('note', sa.JSON,
            
            
            nullable=False, 
            
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
    op.drop_table('medical_equipment_analysis_setting')