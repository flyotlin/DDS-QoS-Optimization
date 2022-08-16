# Case 3
## How to Run
- Run all trials
  `$ time bash run.sh`
- Run one trial
  `$ ansible-playbook -v -i inventory.yaml playbook.yml -e "trialNum=1 config=OMG-Def"`

## About the experiment
論文上的架構圖跟說明，原本是 30 pub - 34 sub - 30 topic，但根據圖示應該是 29 pub - 34 sub - 29 topic。
