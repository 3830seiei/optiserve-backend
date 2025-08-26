from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '10a11c7cfd18'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'mst_user',
        
        sa.Column('user_id', sa.Text,
            primary_key=True, 
            
            nullable=False, 
            
        ),
        
        sa.Column('user_name', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('entity_type', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('entity_relation_id', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('password', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('e_mail', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('phone_number', sa.Text,
            
            
            
            
        ),
        
        sa.Column('mobile_number', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('user_status', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('inactive_reason_code', sa.Integer,
            
            
            
            
        ),
        
        sa.Column('inactive_reason_note', sa.Text,
            
            
            
            
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
    op.drop_table('mst_user')