# Case 2
## About the experiment
論文上的架構圖跟說明，原本是 15 pub - 17 sub - 15 topic，但根據圖示應該是 12 pub - 17 sub - 12 topic。

## About pub/sub src code
使用檔案 `.flag` 同步所有的 pub/sub，`.flag` 中預設值為 0，只有當數值變成 1 才會觸發所有 pub 開始傳送 samples。

> `.flag` 的建立、狀態由 ansible playbook 控制。
