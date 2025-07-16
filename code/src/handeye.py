# handeye.py
import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("HandEye")


class HandEye:
    """像素坐标 ↔ 机械臂坐标  透视/线性混合标定器"""

    def __init__(self, cfg_path: str = "temp/handeye.json") -> None:
        self.cfg_path = Path(cfg_path)
        self.pixel_pts: Optional[np.ndarray] = None
        self.world_pts: Optional[np.ndarray] = None
        self.M: Optional[np.ndarray] = None          # 3×3 透视矩阵
        self._load_or_create()

    # ---------------- 标定 ----------------
    def add_point(self, px: Tuple[int, int], world: Tuple[float, float]) -> None:
        px_arr = np.array([px], dtype=np.float32)
        wl_arr = np.array([world], dtype=np.float32)
        self.pixel_pts = px_arr if self.pixel_pts is None else np.vstack([self.pixel_pts, px_arr])
        self.world_pts = wl_arr if self.world_pts is None else np.vstack([self.world_pts, wl_arr])
        self._calc_matrix()
        self._save()

    def calibrate(self,
                  pixel_list: List[Tuple[int, int]],
                  world_list: List[Tuple[float, float]],
                  *,
                  max_error: float = 2.0) -> None:
        assert len(pixel_list) == len(world_list) >= 2, "点数至少 2"
        self.pixel_pts = np.array(pixel_list, dtype=np.float32)
        self.world_pts = np.array(world_list, dtype=np.float32)

        if len(pixel_list) >= 4:
            self.M, mask = cv2.findHomography(self.pixel_pts, self.world_pts,
                                              cv2.RANSAC, max_error)
            if mask is not None:
                inliers = mask.ravel() == 1
                self.pixel_pts = self.pixel_pts[inliers]
                self.world_pts = self.world_pts[inliers]
            log.info(f"透视标定完成，有效点数 {len(self.pixel_pts)}")
        else:
            log.warning("点数<4，使用线性插值")
            self.M = None
        self._save()

    # ---------------- 坐标映射 ----------------
    def pixel_to_world(self, px: Tuple[int, int]) -> Tuple[float, float]:
        if self.M is not None and len(self.pixel_pts) >= 4:
            pts = np.array([[px]], dtype=np.float32)
            dst = cv2.perspectiveTransform(pts, self.M)[0][0]
            return float(dst[0]), float(dst[1])
        # 线性插值兜底
        x = float(np.interp(px[0], self.pixel_pts[:, 0], self.world_pts[:, 0]))
        y = float(np.interp(px[1], self.pixel_pts[:, 1], self.world_pts[:, 1]))
        return x, y

    # ---------------- 持久化 ----------------
    def _load_or_create(self) -> None:
        if self.cfg_path.exists():
            data = json.loads(self.cfg_path.read_text())
            self.pixel_pts = np.array(data["pixel"], dtype=np.float32)
            self.world_pts = np.array(data["world"], dtype=np.float32)
            self._calc_matrix()
            log.info("已加载标定文件")
        else:
            self.pixel_pts = self.world_pts = None
            self.M = None

    def _calc_matrix(self) -> None:
        if self.pixel_pts is not None and len(self.pixel_pts) >= 4:
            self.M, _ = cv2.findHomography(self.pixel_pts, self.world_pts)

    def _save(self) -> None:
        if self.pixel_pts is None:
            return
        self.cfg_path.parent.mkdir(exist_ok=True)
        json.dump({"pixel": self.pixel_pts.tolist(),
                   "world": self.world_pts.tolist()},
                  self.cfg_path.open("w"), indent=2)