import { expect, test } from "@playwright/test";

test("mobile home page renders in Chinese without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /你好，小小数学家/ })).toBeVisible();
  await expect(page.getByRole("link", { name: "数学小老师首页" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "我想练一练" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "看看我的试卷" })).toBeVisible();

  const overflow = await page.evaluate(() => ({
    viewportWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.viewportWidth);
});

test("welcome action is keyboard-operable and shows the next-step state", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: /看看今天怎么学/ }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "先选一个你想了解的数学单元" })).toBeVisible();
  await expect(page.getByText(/不会记录练习或伪造学习成绩/)).toBeVisible();
});
