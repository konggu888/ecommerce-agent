# Job Monitor

所有长任务统一记录 QUEUED/RUNNING/COMPLETED/FAILED/CANCELLED、总任务数、完成数、当前任务、错误、开始/结束时间和结果位置。

回测、数据同步、采集任务都应使用同一状态模型。前端可轮询状态，也可由 Supabase Realtime 推送。

状态判定：COMPLETED 只允许在 completedTasks === totalTasks 后写入；FAILED 必须保存 error；RUNNING 必须持续更新 updatedAt。
