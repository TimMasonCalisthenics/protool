from infrastructure.persistence.models.system_settings import SystemSetting
from domain.exceptions.base import AppError, ConflictError
from flask import current_app

class SystemService:
    def __init__(self, system_repo):
        self.repo = system_repo
    def get_active_id_product(self):
        return self.repo.get_active_id_product()

    def update_active_id_product(self, product_id):
        return self.repo.update_active_id_product(product_id)
    def update_active_id_draft(self, draft_id):
        return self.repo.update_active_id_draft(draft_id)
