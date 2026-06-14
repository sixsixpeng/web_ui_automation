# -*- coding: utf-8 -*-
"""screenshot_util - Screenshot (Sync + Async)"""
from io import BytesIO

import allure
from PIL import Image, ImageDraw, ImageFont

from utils.log_util import get_logger
from utils.path_util import path_util
from utils.time_util import time_util

logger = get_logger("screenshot_util")


class ScreenshotSyncUtil:
    @staticmethod
    def _get_font(size=14):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

    @staticmethod
    def _overlay_url_bar(img, url=""):
        bar_h, w = 36, img.width
        new = Image.new("RGB", (w, img.height + bar_h), (240, 240, 240))
        d = ImageDraw.Draw(new)
        d.rectangle([0, 0, w, bar_h], fill="#DEE1E6")
        box_m, box_h, box_y = 20, 24, (bar_h - 24) // 2
        d.rounded_rectangle([box_m, box_y, w - box_m, box_y + box_h], radius=12, fill="white")
        d.text((box_m + 16, box_y + 4), url or "about:blank", fill="#3C4043", font=ScreenshotSyncUtil._get_font(12))
        new.paste(img, (0, bar_h))
        return new

    @staticmethod
    def take_window_screenshot(page, name=None, attach_allure=True):
        """截取当前窗口截图"""
        ts = time_util.filename_prefix()
        sp = str(path_util.screenshots_dir / f'{ts}{name or chr(34) + chr(119) + chr(105) + chr(110) + chr(100) + chr(111) + chr(119) + chr(34)}.png')
        b = page.screenshot(full_page=False)
        img = Image.open(BytesIO(b))
        img2 = ScreenshotSyncUtil._overlay_url_bar(img, page.url)
        out = BytesIO();
        img2.save(out, format="PNG");
        rb = out.getvalue()
        with open(sp, "wb") as f: f.write(rb)
        if attach_allure:
            try:
                allure.attach(rb, name=name or "screenshot", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return rb

    async def take_full_page_screenshot(self, page, name=None, attach_allure=True):
        ts = time_util.filename_prefix()
        sp = str(path_util.screenshots_dir / f"{ts}{name or 'fullpage'}.png")
        b = await page.screenshot(full_page=True)
        img = Image.open(BytesIO(b))
        img2 = ScreenshotSyncUtil._overlay_url_bar(img, page.url)
        out = BytesIO();
        img2.save(out, format="PNG");
        rb = out.getvalue()
        with open(sp, "wb") as f: f.write(rb)
        if attach_allure:
            try:
                allure.attach(rb, name=name or "fullpage", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return rb

    async def take_element_screenshot(self, page, selector, name=None, attach_allure=True):
        ts = time_util.filename_prefix()
        el = page.locator(selector)
        b = await el.screenshot()
        sp = str(path_util.screenshots_dir / f"{ts}{name or 'element'}.png")
        with open(sp, "wb") as f: f.write(b)
        if attach_allure:
            try:
                allure.attach(b, name=name or f"el_{selector}", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return b

    @staticmethod
    def take_full_page_screenshot(page, name=None, attach_allure=True):
        """截取整页长截图"""
        ts = time_util.filename_prefix()
        sp = str(path_util.screenshots_dir / f"{ts}{name or chr(102) + chr(117) + chr(108) + chr(108) + chr(112) + chr(97) + chr(103) + chr(101)}.png")
        b = page.screenshot(full_page=True)
        img = Image.open(BytesIO(b))
        img2 = ScreenshotSyncUtil._overlay_url_bar(img, page.url)
        out = BytesIO();
        img2.save(out, format="PNG");
        rb = out.getvalue()
        with open(sp, "wb") as f: f.write(rb)
        if attach_allure:
            try:
                allure.attach(rb, name=name or "fullpage", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return rb

    @staticmethod
    def take_element_screenshot(page, selector, name=None, attach_allure=True):
        """截取元素截图"""
        ts = time_util.filename_prefix()
        el = page.locator(selector)
        b = el.screenshot()
        sp = str(path_util.screenshots_dir / f"{ts}{name or 'element'}.png")
        with open(sp, "wb") as f: f.write(b)
        if attach_allure:
            try:
                allure.attach(b, name=name or f"el_{selector}", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return b


class ScreenshotAsyncUtil:
    async def take_window_screenshot(self, page, name=None, attach_allure=True):
        ts = time_util.filename_prefix()
        sp = str(path_util.screenshots_dir / f'{ts}{name or chr(34) + chr(119) + chr(105) + chr(110) + chr(100) + chr(111) + chr(119) + chr(34)}.png')
        b = await page.screenshot(full_page=False)
        img = Image.open(BytesIO(b))
        img2 = ScreenshotSyncUtil._overlay_url_bar(img, page.url)
        out = BytesIO();
        img2.save(out, format="PNG");
        rb = out.getvalue()
        with open(sp, "wb") as f: f.write(rb)
        if attach_allure:
            try:
                allure.attach(rb, name=name or "screenshot", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return rb

    async def take_full_page_screenshot(self, page, name=None, attach_allure=True):
        ts = time_util.filename_prefix()
        sp = str(path_util.screenshots_dir / f"{ts}{name or 'fullpage'}.png")
        b = await page.screenshot(full_page=True)
        img = Image.open(BytesIO(b))
        img2 = ScreenshotSyncUtil._overlay_url_bar(img, page.url)
        out = BytesIO();
        img2.save(out, format="PNG");
        rb = out.getvalue()
        with open(sp, "wb") as f: f.write(rb)
        if attach_allure:
            try:
                allure.attach(rb, name=name or "fullpage", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return rb

    async def take_element_screenshot(self, page, selector, name=None, attach_allure=True):
        ts = time_util.filename_prefix()
        el = page.locator(selector)
        b = await el.screenshot()
        sp = str(path_util.screenshots_dir / f"{ts}{name or 'element'}.png")
        with open(sp, "wb") as f: f.write(b)
        if attach_allure:
            try:
                allure.attach(b, name=name or f"el_{selector}", attachment_type=allure.attachment_type.PNG)
            except:
                pass
        return b
