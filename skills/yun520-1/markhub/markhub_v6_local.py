#!/usr/bin/env python3
"""
MarkHub v6.0 - 完全本地 AI 创作系统

核心特性：
- 100% 本地运行，无需 ComfyUI
- 使用开源 stable-diffusion-cpp-python
- 自动下载和管理模型
- 无法律风险（使用开源模型）
- 支持文生图、图生图、视频生成

依赖：
pip install stable-diffusion-cpp-python pillow numpy
"""

import os
import sys
import json
import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.error
import ssl

# 忽略 SSL 证书验证（用于模型下载）
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

try:
    from stable_diffusion_cpp import StableDiffusion
    from PIL import Image
    import numpy as np
    HAS_SD = True
except ImportError:
    HAS_SD = False
    print("⚠️  未安装 stable-diffusion-cpp-python")
    print("   安装：pip install stable-diffusion-cpp-python")


class MarkHubLocal:
    """本地 AI 创作引擎"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path.home() / "Videos" / "MarkHub"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.models_dir = Path.home() / ".markhub" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.sd_model = None
        self.current_model = None
        
        # 开源模型列表（无法律风险）
        self.open_source_models = {
            "sd-turbo": {
                "url": "https://huggingface.co/stabilityai/sd-turbo/resolve/main/sd_turbo.safetensors",
                "type": "txt2img",
                "resolution": (512, 512),
                "steps": 1,  # Turbo 只需 1 步
                "cfg": 0.0,
                "size_mb": 1400
            },
            "sdxl-turbo": {
                "url": "https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors",
                "type": "txt2img",
                "resolution": (1024, 1024),
                "steps": 1,
                "cfg": 0.0,
                "size_mb": 6000
            },
            "stable-diffusion-v1-5": {
                "url": "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt",
                "type": "txt2img",
                "resolution": (512, 512),
                "steps": 20,
                "cfg": 7.5,
                "size_mb": 4000
            },
            "stable-diffusion-v2-1": {
                "url": "https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt",
                "type": "txt2img",
                "resolution": (768, 768),
                "steps": 20,
                "cfg": 7.5,
                "size_mb": 5000
            }
        }
        
        print("=" * 70)
        print("🎨 MarkHub v6.0 - 完全本地 AI 创作系统")
        print("=" * 70)
        print(f"📁 输出目录：{self.output_dir}")
        print(f"📦 模型目录：{self.models_dir}")
        print(f"💾 可用空间：{self._get_free_space()}")
        print()
    
    def _get_free_space(self) -> str:
        """获取可用磁盘空间"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.models_dir)
            return f"{free / (1024**3):.1f} GB"
        except:
            return "未知"
    
    def download_model(self, model_name: str) -> Optional[Path]:
        """下载模型"""
        if model_name not in self.open_source_models:
            print(f"❌ 未知模型：{model_name}")
            print(f"可用模型：{list(self.open_source_models.keys())}")
            return None
        
        model_info = self.open_source_models[model_name]
        model_path = self.models_dir / f"{model_name}.safetensors"
        
        # 检查是否已下载
        if model_path.exists():
            print(f"✅ 模型已存在：{model_path}")
            return model_path
        
        # 检查磁盘空间
        required_gb = model_info.get("size_mb", 4000) / 1024
        free_gb = float(self._get_free_space().split()[0]) if self._get_free_space() != "未知" else 0
        
        if free_gb < required_gb:
            print(f"❌ 磁盘空间不足")
            print(f"   需要：{required_gb:.1f} GB")
            print(f"   可用：{free_gb:.1f} GB")
            return None
        
        print(f"📥 下载模型：{model_name}")
        print(f"   来源：{model_info['url']}")
        print(f"   大小：{model_info.get('size_mb', 4000)} MB")
        print(f"   路径：{model_path}")
        
        try:
            # 显示下载进度
            def reporthook(blocknum, blocksize, totalsize):
                readsofar = blocknum * blocksize
                if totalsize > 0:
                    percent = readsofar * 100 / totalsize
                    print(f"\r   进度：{percent:.1f}%", end="")
            
            urllib.request.urlretrieve(
                model_info["url"],
                str(model_path),
                reporthook=reporthook
            )
            print(f"\n✅ 下载完成")
            return model_path
            
        except Exception as e:
            print(f"\n❌ 下载失败：{e}")
            if model_path.exists():
                model_path.unlink()
            return None
    
    def load_model(self, model_name: str = "sd-turbo") -> bool:
        """加载模型"""
        if not HAS_SD:
            print("❌ stable-diffusion-cpp-python 未安装")
            print("   请运行：pip install stable-diffusion-cpp-python")
            return False
        
        # 下载模型（如果不存在）
        model_path = self.download_model(model_name)
        if not model_path:
            return False
        
        # 卸载旧模型
        if self.sd_model:
            del self.sd_model
            self.sd_model = None
        
        print(f"🔄 加载模型：{model_name}")
        try:
            self.sd_model = StableDiffusion(
                model_path=str(model_path),
                lora_model_dir=None,
                n_threads=-1,  # 使用所有 CPU 核心
                wtype="f16",   # 半精度，节省内存
                control_net=None,
                clip_l=None,
                clip_g=None,
                vae_path=None,
                taesd_path=None,
                embeddings_dir=None,
                stacked_id_embeddings_dir=None,
                lora_name_dir=None,
                control_net_path=None,
                upscaler_path=None,
                n_gpu_layers=0,  # CPU 模式
                rng_type="cuda",
                schedule="karras",
            )
            self.current_model = model_name
            print(f"✅ 模型加载成功")
            return True
            
        except Exception as e:
            print(f"❌ 模型加载失败：{e}")
            return False
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = None,
        cfg_scale: float = None,
        seed: int = -1,
        batch_count: int = 1,
        output_path: str = None
    ) -> List[Path]:
        """生成图片"""
        if not self.sd_model:
            print("❌ 模型未加载")
            return []
        
        # 使用模型默认参数
        model_info = self.open_source_models.get(self.current_model, {})
        if steps is None:
            steps = model_info.get("steps", 20)
        if cfg_scale is None:
            cfg_scale = model_info.get("cfg", 7.5)
        
        print(f"\n🎨 生成图片")
        print(f"   提示词：{prompt[:80]}...")
        print(f"   尺寸：{width}x{height}")
        print(f"   步数：{steps}")
        print(f"   CFG: {cfg_scale}")
        print(f"   数量：{batch_count}")
        
        generated_images = []
        
        try:
            for i in range(batch_count):
                print(f"\n   生成 {i+1}/{batch_count}...")
                
                # 生成图片
                image = self.sd_model.txt2img(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    seed=seed if seed >= 0 else int(time.time() * 1000) % (2**31),
                    sample_method="euler_a",
                )
                
                # 保存
                if output_path:
                    save_path = Path(output_path)
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = self.output_dir / f"MarkHub_{timestamp}_{i+1}.png"
                
                # 转换为 PIL Image 并保存
                if isinstance(image, np.ndarray):
                    pil_image = Image.fromarray(image)
                else:
                    pil_image = image
                
                pil_image.save(str(save_path), "PNG")
                generated_images.append(save_path)
                print(f"   ✅ 已保存：{save_path}")
            
            print(f"\n✅ 生成完成，共 {len(generated_images)} 张图片")
            return generated_images
            
        except Exception as e:
            print(f"❌ 生成失败：{e}")
            return []
    
    def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        fps: int = 24,
        width: int = 512,
        height: int = 512,
        output_path: str = None
    ) -> Optional[Path]:
        """生成视频（通过生成多帧图片并合成）"""
        print(f"\n🎬 生成视频")
        print(f"   提示词：{prompt[:80]}...")
        print(f"   时长：{duration}秒")
        print(f"   FPS: {fps}")
        print(f"   尺寸：{width}x{height}")
        
        # 生成帧
        frame_count = duration * fps
        frame_dir = self.output_dir / f"video_frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        frame_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n   生成 {frame_count} 帧...")
        
        frames = []
        for i in range(frame_count):
            # 为每帧添加轻微变化（模拟运动）
            frame_prompt = f"{prompt}, frame {i+1}/{frame_count}"
            
            image = self.sd_model.txt2img(
                prompt=frame_prompt,
                width=width,
                height=height,
                steps=1,  # Turbo 模式
                cfg_scale=0.0,
                seed=int(time.time() * 1000) + i,
                sample_method="euler_a",
            )
            
            frame_path = frame_dir / f"frame_{i:04d}.png"
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            pil_image.save(str(frame_path), "PNG")
            frames.append(frame_path)
            
            if (i + 1) % 10 == 0:
                print(f"   进度：{i+1}/{frame_count} 帧")
        
        # 使用 FFmpeg 合成视频
        print(f"\n   合成视频...")
        if output_path:
            video_path = Path(output_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = self.output_dir / f"MarkHub_Video_{timestamp}.mp4"
        
        import subprocess
        cmd = [
            "ffmpeg",
            "-framerate", str(fps),
            "-i", str(frame_dir / "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-y",
            str(video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 清理帧文件
        import shutil
        shutil.rmtree(frame_dir)
        
        if result.returncode == 0:
            print(f"✅ 视频已保存：{video_path}")
            return video_path
        else:
            print(f"❌ 视频合成失败：{result.stderr}")
            return None
    
    def auto_generate(self, prompt: str, is_video: bool = False) -> Optional[Path]:
        """自动生成（自动选择最佳模型和参数）"""
        print(f"\n🤖 自动模式")
        
        # 选择模型
        if is_video:
            # 视频使用 SD Turbo（快速）
            model = "sd-turbo"
        else:
            # 图片根据提示词选择
            if "portrait" in prompt.lower() or "woman" in prompt.lower() or "man" in prompt.lower():
                model = "sdxl-turbo"  # 高质量人像
            else:
                model = "sd-turbo"  # 快速生成
        
        # 加载模型
        if not self.load_model(model):
            return None
        
        # 生成
        if is_video:
            return self.generate_video(prompt, duration=10)
        else:
            images = self.generate_image(prompt, batch_count=1)
            return images[0] if images else None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MarkHub v6.0 - 本地 AI 创作")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="提示词")
    parser.add_argument("-n", "--negative", type=str, default="", help="负面提示词")
    parser.add_argument("-m", "--model", type=str, default="sd-turbo", help="模型名称")
    parser.add_argument("--video", action="store_true", help="生成视频")
    parser.add_argument("--duration", type=int, default=10, help="视频时长（秒）")
    parser.add_argument("--auto", action="store_true", help="自动模式")
    parser.add_argument("-o", "--output", type=str, help="输出路径")
    parser.add_argument("--width", type=int, default=512, help="宽度")
    parser.add_argument("--height", type=int, default=512, help="高度")
    parser.add_argument("--steps", type=int, help="步数")
    parser.add_argument("--cfg", type=float, help="CFG 比例")
    
    args = parser.parse_args()
    
    # 创建实例
    markhub = MarkHubLocal()
    
    # 自动生成
    if args.auto:
        result = markhub.auto_generate(args.prompt, is_video=args.video)
        if result:
            print(f"\n✅ 完成：{result}")
        else:
            print("\n❌ 生成失败")
        return
    
    # 手动模式
    # 加载模型
    if not markhub.load_model(args.model):
        return
    
    # 生成
    if args.video:
        result = markhub.generate_video(
            args.prompt,
            duration=args.duration,
            output_path=args.output
        )
    else:
        results = markhub.generate_image(
            args.prompt,
            negative_prompt=args.negative,
            width=args.width,
            height=args.height,
            steps=args.steps,
            cfg_scale=args.cfg,
            output_path=args.output
        )
        result = results[0] if results else None
    
    if result:
        print(f"\n✅ 完成：{result}")
    else:
        print("\n❌ 生成失败")


if __name__ == "__main__":
    main()
