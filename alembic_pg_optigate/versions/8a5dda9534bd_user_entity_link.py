from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8a5dda9534bd'
down_revision = '10a11c7cfd18'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user_entity_link',
        
        sa.Column('entity_type', sa.Integer,
            primary_key=True, 
            
            nullable=False, 
            
        ),
        
        sa.Column('entity_relation_id', sa.Integer,
            primary_key=True, 
            
            nullable=False, 
            
        ),
        
        sa.Column('entity_name', sa.Text,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('entity_address_postal_code', sa.Text,
            
            
            
            
        ),
        
        sa.Column('entity_address_prefecture', sa.Text,
            
            
            
            
        ),
        
        sa.Column('entity_address_city', sa.Text,
            
            
            
            
        ),
        
        sa.Column('entity_address_line1', sa.Text,
            
            
            
            
        ),
        
        sa.Column('entity_address_line2', sa.Text,
            
            
            
            
        ),
        
        sa.Column('entity_phone_number', sa.Text,
            
            
            
            
        ),
        
        sa.Column('notification_email_list', sa.JSON,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('count_reportout_classification', sa.Integer,
            
            
            nullable=False, 
            
        ),
        
        sa.Column('analiris_classification_level', sa.Integer,
            
            
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
    op.drop_table('user_entity_link')