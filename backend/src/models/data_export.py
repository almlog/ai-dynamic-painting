"""
Data export/import models for managing data transfer operations.
Supports multiple formats, scheduling, and security features.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from enum import Enum

Base = declarative_base()


class ExportType(str, Enum):
    """Enumeration of export types"""
    ANALYTICS = "analytics"
    METRICS = "metrics"
    DASHBOARDS = "dashboards"
    SYSTEM_DATA = "system_data"
    BACKUP = "backup"
    CUSTOM = "custom"


class ExportFormat(str, Enum):
    """Enumeration of export formats"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    XML = "xml"
    PARQUET = "parquet"
    SQL = "sql"


class ExportStatusEnum(str, Enum):
    """Enumeration of export status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED_WITH_ERRORS = "completed_with_errors"


class ImportStatusEnum(str, Enum):
    """Enumeration of import status"""
    PENDING = "pending"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED_WITH_ERRORS = "completed_with_errors"


class DataExport(Base):
    """SQLAlchemy model for storing export operations"""
    __tablename__ = "data_exports"
    
    id = Column(Integer, primary_key=True)
    export_id = Column(String(255), nullable=False, unique=True, index=True)
    export_name = Column(String(255), nullable=False)
    export_type = Column(String(50), nullable=False)
    export_format = Column(String(20), nullable=False)
    
    # Data sources and configuration
    data_sources = Column(JSON)  # List of data sources to export
    export_config = Column(JSON)  # Export configuration parameters
    filters = Column(JSON)  # Data filtering criteria
    
    # File information
    file_path = Column(String(500))
    file_size_bytes = Column(Integer, default=0)
    file_hash = Column(String(64))  # SHA-256 hash
    compression_type = Column(String(20))
    
    # Status and progress
    status = Column(String(30), default="pending")
    progress_percentage = Column(Float, default=0.0)
    records_exported = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Metadata
    created_by = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Security and access
    access_level = Column(String(20), default="private")
    encryption_enabled = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime)
    
    def __init__(self, export_id: str, export_name: str, export_type: str,
                 data_sources: List[str], export_format: str, created_by: str,
                 export_config: Dict[str, Any] = None, file_path: str = None):
        self.export_id = export_id
        self.export_name = export_name
        self.export_type = export_type
        self.data_sources = data_sources
        self.export_format = export_format
        self.created_by = created_by
        self.export_config = export_config or {}
        self.file_path = file_path
        self.filters = {}
        self.status = ExportStatusEnum.PENDING.value
        self.progress_percentage = 0.0
        self.records_exported = 0
        self.created_at = datetime.now()
        self.access_level = "private"
        self.encryption_enabled = False
        self.download_count = 0
    
    def start_processing(self):
        """Mark export as started"""
        self.status = ExportStatusEnum.PROCESSING.value
        self.started_at = datetime.now()
    
    def update_progress(self, percentage: float, records_count: int = None):
        """Update export progress"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        if records_count is not None:
            self.records_exported = records_count
    
    def complete_export(self, file_path: str, file_size: int, records_count: int):
        """Mark export as completed"""
        self.status = ExportStatusEnum.COMPLETED.value
        self.progress_percentage = 100.0
        self.file_path = file_path
        self.file_size_bytes = file_size
        self.records_exported = records_count
        self.completed_at = datetime.now()
        # Set expiration (default 7 days)
        self.expires_at = datetime.now() + timedelta(days=7)
    
    def fail_export(self, error_message: str):
        """Mark export as failed"""
        self.status = ExportStatusEnum.FAILED.value
        self.error_message = error_message
        self.completed_at = datetime.now()
    
    def record_download(self):
        """Record a download of the exported file"""
        self.download_count += 1
        self.last_downloaded_at = datetime.now()


class DataImport(Base):
    """SQLAlchemy model for storing import operations"""
    __tablename__ = "data_imports"
    
    id = Column(Integer, primary_key=True)
    import_id = Column(String(255), nullable=False, unique=True, index=True)
    import_name = Column(String(255), nullable=False)
    import_type = Column(String(50), nullable=False)
    source_format = Column(String(20), nullable=False)
    
    # Source information
    source_file_path = Column(String(500))
    source_file_size = Column(Integer)
    source_file_hash = Column(String(64))
    
    # Import configuration
    data_mapping = Column(JSON)  # Field mapping configuration
    validation_rules = Column(JSON)  # Data validation rules
    import_config = Column(JSON)  # Import configuration parameters
    
    # Status and progress
    status = Column(String(30), default="pending")
    progress_percentage = Column(Float, default=0.0)
    records_processed = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    validation_errors = Column(JSON)  # List of validation errors
    
    # Metadata
    created_by = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __init__(self, import_id: str, import_name: str, import_type: str,
                 source_format: str, created_by: str, source_file_path: str = None,
                 data_mapping: Dict[str, str] = None, validation_rules: Dict[str, Any] = None):
        self.import_id = import_id
        self.import_name = import_name
        self.import_type = import_type
        self.source_format = source_format
        self.created_by = created_by
        self.source_file_path = source_file_path
        self.data_mapping = data_mapping or {}
        self.validation_rules = validation_rules or {}
        self.import_config = {}
        self.status = ImportStatusEnum.PENDING.value
        self.progress_percentage = 0.0
        self.records_processed = 0
        self.records_imported = 0
        self.records_failed = 0
        self.validation_errors = []
        self.created_at = datetime.now()
    
    def start_processing(self):
        """Mark import as started"""
        self.status = ImportStatusEnum.PROCESSING.value
        self.started_at = datetime.now()
    
    def update_progress(self, percentage: float, processed: int, imported: int, failed: int):
        """Update import progress"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        self.records_processed = processed
        self.records_imported = imported
        self.records_failed = failed
    
    def add_validation_error(self, row_number: int, field: str, error: str, value: Any = None):
        """Add a validation error"""
        if not self.validation_errors:
            self.validation_errors = []
        
        error_entry = {
            "row": row_number,
            "field": field,
            "error": error,
            "value": str(value) if value is not None else None,
            "timestamp": datetime.now().isoformat()
        }
        self.validation_errors.append(error_entry)
    
    def complete_import(self):
        """Mark import as completed"""
        if self.records_failed > 0:
            self.status = ImportStatusEnum.COMPLETED_WITH_ERRORS.value
        else:
            self.status = ImportStatusEnum.COMPLETED.value
        self.progress_percentage = 100.0
        self.completed_at = datetime.now()
    
    def fail_import(self, error_message: str):
        """Mark import as failed"""
        self.status = ImportStatusEnum.FAILED.value
        self.completed_at = datetime.now()
        if not self.validation_errors:
            self.validation_errors = []
        self.validation_errors.append({
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "type": "system_error"
        })


class ExportSchedule(Base):
    """SQLAlchemy model for storing scheduled exports"""
    __tablename__ = "export_schedules"
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(String(255), nullable=False, unique=True, index=True)
    schedule_name = Column(String(255), nullable=False)
    export_config = Column(JSON, nullable=False)  # Export configuration template
    
    # Schedule configuration
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly
    schedule_time = Column(String(10))  # HH:MM format
    timezone = Column(String(50), default="UTC")
    enabled = Column(Boolean, default=True)
    
    # Retention policy
    retention_days = Column(Integer, default=30)
    max_exports = Column(Integer, default=10)
    
    # Metadata
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_executed = Column(DateTime)
    next_execution = Column(DateTime)
    execution_count = Column(Integer, default=0)
    
    def __init__(self, schedule_id: str, schedule_name: str, export_config: Dict[str, Any],
                 frequency: str, created_by: str, schedule_time: str = None):
        self.schedule_id = schedule_id
        self.schedule_name = schedule_name
        self.export_config = export_config
        self.frequency = frequency
        self.created_by = created_by
        self.schedule_time = schedule_time
        self.timezone = "UTC"
        self.enabled = True
        self.retention_days = 30
        self.max_exports = 10
        self.created_at = datetime.now()
        self.execution_count = 0
    
    def record_execution(self):
        """Record a schedule execution"""
        self.last_executed = datetime.now()
        self.execution_count += 1
        # Calculate next execution time based on frequency
        if self.frequency == "daily":
            self.next_execution = datetime.now() + timedelta(days=1)
        elif self.frequency == "weekly":
            self.next_execution = datetime.now() + timedelta(weeks=1)
        elif self.frequency == "monthly":
            self.next_execution = datetime.now() + timedelta(days=30)


class ExportTemplate(Base):
    """SQLAlchemy model for storing export templates"""
    __tablename__ = "export_templates"
    
    id = Column(Integer, primary_key=True)
    template_id = Column(String(255), nullable=False, unique=True, index=True)
    template_name = Column(String(255), nullable=False)
    description = Column(Text)
    template_type = Column(String(50), nullable=False)  # export, import
    category = Column(String(50))
    
    # Template configuration
    template_config = Column(JSON, nullable=False)
    default_values = Column(JSON)
    required_parameters = Column(JSON)
    
    # Access and sharing
    is_public = Column(Boolean, default=False)
    created_by = Column(String(255), nullable=False)
    shared_with = Column(JSON)  # List of user IDs with access
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, template_id: str, template_name: str, template_type: str,
                 template_config: Dict[str, Any], created_by: str,
                 description: str = None, category: str = None):
        self.template_id = template_id
        self.template_name = template_name
        self.description = description
        self.template_type = template_type
        self.category = category
        self.template_config = template_config
        self.created_by = created_by
        self.default_values = {}
        self.required_parameters = []
        self.is_public = False
        self.shared_with = []
        self.usage_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def record_usage(self):
        """Record template usage"""
        self.usage_count += 1
        self.last_used = datetime.now()
        self.updated_at = datetime.now()


# Pydantic models for API and data validation

class ExportConfig(BaseModel):
    """Pydantic model for export configuration"""
    name: str = Field(..., description="Export name")
    type: ExportType = Field(..., description="Export type")
    format: ExportFormat = Field(..., description="Export format")
    data_sources: List[str] = Field(..., description="Data sources to export")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    filters: Dict[str, Any] = Field({}, description="Additional filters")
    include_metadata: bool = Field(True, description="Include metadata in export")
    compression: bool = Field(False, description="Enable compression")
    encryption: bool = Field(False, description="Enable encryption")
    
    class Config:
        from_attributes = True


class ImportConfig(BaseModel):
    """Pydantic model for import configuration"""
    name: str = Field(..., description="Import name")
    type: str = Field(..., description="Import type")
    source_format: ExportFormat = Field(..., description="Source format")
    file_path: Optional[str] = Field(None, description="Source file path")
    file_content: Optional[List[Dict[str, Any]]] = Field(None, description="Direct data content")
    data_mapping: Dict[str, str] = Field({}, description="Field mapping")
    validation_rules: Dict[str, Any] = Field({}, description="Validation rules")
    conflict_resolution: str = Field("skip", description="Conflict resolution strategy")
    batch_size: int = Field(1000, description="Import batch size")
    
    class Config:
        from_attributes = True


class ExportStatus(BaseModel):
    """Pydantic model for export status"""
    export_id: str
    status: str
    progress_percentage: float
    records_exported: int
    file_size_bytes: Optional[int]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ImportStatus(BaseModel):
    """Pydantic model for import status"""
    import_id: str
    status: str
    progress_percentage: float
    records_processed: int
    records_imported: int
    records_failed: int
    validation_errors: List[Dict[str, Any]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TemplateConfig(BaseModel):
    """Pydantic model for template configuration"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    type: str = Field(..., description="Template type (export/import)")
    template: Dict[str, Any] = Field(..., description="Template configuration")
    category: Optional[str] = Field(None, description="Template category")
    is_public: bool = Field(False, description="Public template flag")
    
    class Config:
        from_attributes = True


class BackupConfig(BaseModel):
    """Pydantic model for backup configuration"""
    name: str = Field(..., description="Backup name")
    type: str = Field("backup", description="Backup type")
    scope: str = Field(..., description="Backup scope")
    include: List[str] = Field(..., description="Data types to include")
    exclude: List[str] = Field([], description="Data types to exclude")
    compression: str = Field("gzip", description="Compression type")
    encryption: bool = Field(False, description="Enable encryption")
    encryption_key: Optional[str] = Field(None, description="Encryption key")
    
    class Config:
        from_attributes = True


class RestoreConfig(BaseModel):
    """Pydantic model for restore configuration"""
    backup_id: str = Field(..., description="Backup ID to restore from")
    restore_scope: str = Field(..., description="Restore scope")
    include: List[str] = Field(..., description="Data types to restore")
    conflict_resolution: str = Field("merge", description="Conflict resolution strategy")
    dry_run: bool = Field(False, description="Dry run mode")
    
    class Config:
        from_attributes = True