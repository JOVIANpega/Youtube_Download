#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg 管理器
偵測、下載/安裝（Windows）、合併參數
"""

import os
import sys
import subprocess
import platform
import shutil
try:
    import requests
except ImportError:
    print("警告: requests 未安裝，FFmpeg 自動下載功能將不可用")
    print("請運行: pip install requests")
    requests = None
import zipfile
from typing import Optional, Tuple
from utils.path_utils import get_resource_path, ensure_directory
from logging_config import get_logger

logger = get_logger(__name__)

class FFmpegManager:
    """FFmpeg 管理器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.ffmpeg_path = None
        self.ffprobe_path = None
        self._detect_ffmpeg()
        
    def _detect_ffmpeg(self):
        """檢測 FFmpeg"""
        # 檢查系統 PATH
        ffmpeg_cmd = 'ffmpeg.exe' if self.system == 'windows' else 'ffmpeg'
        ffprobe_cmd = 'ffprobe.exe' if self.system == 'windows' else 'ffprobe'
        
        self.ffmpeg_path = shutil.which(ffmpeg_cmd)
        self.ffprobe_path = shutil.which(ffprobe_cmd)
        
        if self.ffmpeg_path and self.ffprobe_path:
            logger.info(f"找到系統 FFmpeg: {self.ffmpeg_path}")
            return
            
        # 檢查本地 assets 目錄
        if self.system == 'windows':
            local_ffmpeg = get_resource_path('assets/ffmpeg/ffmpeg.exe')
            local_ffprobe = get_resource_path('assets/ffmpeg/ffprobe.exe')
            
            if os.path.exists(local_ffmpeg) and os.path.exists(local_ffprobe):
                self.ffmpeg_path = local_ffmpeg
                self.ffprobe_path = local_ffprobe
                logger.info(f"找到本地 FFmpeg: {self.ffmpeg_path}")
                return
                
        logger.warning("未找到 FFmpeg")
        
    def is_available(self) -> bool:
        """檢查 FFmpeg 是否可用"""
        return self.ffmpeg_path is not None and self.ffprobe_path is not None
        
    def get_ffmpeg_path(self) -> Optional[str]:
        """獲取 FFmpeg 路徑"""
        return self.ffmpeg_path
        
    def get_ffprobe_path(self) -> Optional[str]:
        """獲取 FFprobe 路徑"""
        return self.ffprobe_path
        
    def get_version(self) -> Optional[str]:
        """獲取 FFmpeg 版本"""
        if not self.is_available():
            return None
            
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 解析版本資訊
                lines = result.stdout.split('\n')
                if lines:
                    version_line = lines[0]
                    if 'ffmpeg version' in version_line:
                        return version_line.split('ffmpeg version')[1].split()[0]
                        
        except Exception as e:
            logger.error(f"獲取 FFmpeg 版本失敗: {e}")
            
        return None
        
    def test_functionality(self) -> Tuple[bool, str]:
        """測試 FFmpeg 功能"""
        if not self.is_available():
            return False, "FFmpeg 不可用"
            
        try:
            # 測試基本功能
            result = subprocess.run(
                [self.ffmpeg_path, '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                 '-f', 'null', '-'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, "FFmpeg 功能正常"
            else:
                return False, f"FFmpeg 測試失敗: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "FFmpeg 測試超時"
        except Exception as e:
            return False, f"FFmpeg 測試錯誤: {str(e)}"
            
    def download_ffmpeg_windows(self, progress_callback=None) -> bool:
        """下載 FFmpeg (Windows)"""
        if self.system != 'windows':
            logger.error("僅支援 Windows 自動下載")
            return False
            
        if requests is None:
            logger.error("requests 未安裝，無法下載 FFmpeg")
            return False
            
        try:
            # FFmpeg 下載 URL (使用 gyan.dev 的構建)
            ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            
            # 創建下載目錄
            download_dir = get_resource_path('assets/ffmpeg')
            ensure_directory(download_dir)
            
            zip_path = os.path.join(download_dir, 'ffmpeg.zip')
            
            logger.info("開始下載 FFmpeg...")
            
            # 下載檔案
            response = requests.get(ffmpeg_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress, f"下載中... {downloaded}/{total_size}")
                            
            logger.info("FFmpeg 下載完成，開始解壓...")
            
            # 解壓檔案
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 找到 bin 目錄中的執行檔
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith(('ffmpeg.exe', 'ffprobe.exe')):
                        # 提取到目標目錄
                        file_info.filename = os.path.basename(file_info.filename)
                        zip_ref.extract(file_info, download_dir)
                        
            # 清理下載的 zip 檔案
            os.remove(zip_path)
            
            # 重新檢測
            self._detect_ffmpeg()
            
            if self.is_available():
                logger.info("FFmpeg 安裝成功")
                return True
            else:
                logger.error("FFmpeg 安裝失敗")
                return False
                
        except Exception as e:
            logger.error(f"下載 FFmpeg 失敗: {e}")
            return False
            
    def merge_video_audio(self, video_path: str, audio_path: str, 
                         output_path: str, progress_callback=None) -> bool:
        """合併視頻和音頻"""
        if not self.is_available():
            logger.error("FFmpeg 不可用，無法合併")
            return False
            
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-y',  # 覆蓋輸出檔案
                output_path
            ]
            
            logger.info(f"開始合併: {video_path} + {audio_path} -> {output_path}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 監控進度
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                    
                if output and progress_callback:
                    # 解析 FFmpeg 進度輸出
                    if 'time=' in output:
                        try:
                            time_str = output.split('time=')[1].split()[0]
                            progress_callback(0, f"合併中... {time_str}")
                        except:
                            pass
                            
            return_code = process.poll()
            
            if return_code == 0:
                logger.info("合併完成")
                return True
            else:
                stderr = process.stderr.read()
                logger.error(f"合併失敗: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"合併過程發生錯誤: {e}")
            return False
            
    def convert_format(self, input_path: str, output_path: str, 
                      format_options: dict = None, progress_callback=None) -> bool:
        """轉換格式"""
        if not self.is_available():
            logger.error("FFmpeg 不可用，無法轉換")
            return False
            
        try:
            cmd = [self.ffmpeg_path, '-i', input_path]
            
            # 添加格式選項
            if format_options:
                for key, value in format_options.items():
                    cmd.extend([f'-{key}', str(value)])
                    
            cmd.extend(['-y', output_path])
            
            logger.info(f"開始轉換: {input_path} -> {output_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1小時超時
            )
            
            if result.returncode == 0:
                logger.info("轉換完成")
                return True
            else:
                logger.error(f"轉換失敗: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("轉換超時")
            return False
        except Exception as e:
            logger.error(f"轉換過程發生錯誤: {e}")
            return False
            
    def get_media_info(self, file_path: str) -> dict:
        """獲取媒體檔案資訊"""
        if not self.is_available():
            return {}
            
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                logger.error(f"獲取媒體資訊失敗: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"獲取媒體資訊錯誤: {e}")
            return {}