from pydantic import BaseModel, Field, RootModel
from typing import List, Optional,Union,Dict
from datetime import datetime


class WorkspaceRequest(BaseModel):
    """工作区请求"""
    path: str = Field(..., description="工作目录路径")


class WorkspaceResponse(BaseModel):
    """工作区响应"""
    status: str = Field(..., description="状态，'success'或'error'")
    workspace: Optional[str] = Field(None, description="工作目录路径")
    error: Optional[str] = Field(None, description="错误信息")


class FileItem(BaseModel):
    """文件项"""
    name: str = Field(..., description="文件名")
    path: str = Field(..., description="相对路径")
    type: str = Field(..., description="类型，'file'")
    size: int = Field(..., description="文件大小（字节）")
    modified: datetime = Field(..., description="修改时间")
    extension: Optional[str] = Field(None, description="文件扩展名")


class DirectoryItem(BaseModel):
    """目录项"""
    name: str = Field(..., description="目录名")
    path: str = Field(..., description="相对路径")
    type: str = Field(..., description="类型，'directory'")
    modified: datetime = Field(..., description="修改时间")
    children: Optional[List["FileSystemItem"]] = Field(None, description="子项")


class FileSystemItem(RootModel):
    """文件系统项，可以是文件或目录"""
    root: Union[FileItem, DirectoryItem]


class FilePreview(BaseModel):
    """文件预览"""
    name: str = Field(..., description="文件名")
    path: str = Field(..., description="相对路径")
    type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小（字节）")
    content: str = Field(..., description="文件内容")
    is_binary: bool = Field(False, description="是否为二进制文件")
    is_truncated: bool = Field(False, description="内容是否被截断")
    encoding: Optional[str] = Field(None, description="文件编码")
    preview_type: Optional[str] = Field("text", description="预览类型，如'text'、'image'、'excel'等")
    base64_data: Optional[str] = Field(None, description="Base64编码的文件数据，用于图片等二进制文件")
    structured_data: Optional[Dict] = Field(None, description="结构化数据，用于Excel等表格文件")