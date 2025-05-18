# AutoPlan

## 1. 概述

这是一个多智能体开源个人项目

## 2. 快速开始

首先 clone 项目

```ssh
git clone git@github.com:JustinChen719/auto-plan.git
```

安装环境依赖

```ssh
conda install --name auto-plan --file environment.yaml
```

配置 ```.env``` 文件，十分简单，只需要填写API_KEY、BASE_URL

```text
API_KEY=********
BASE_URL=https://dashscope.aliyuncs.com/***
```

从```main.py```入口文件启动项目就可以开始体验和二次开发多智能体了！