var returnStructure = [
  {
    "deviceId": 12346,
    // 摄像头id
    "taskId": 12346,
    // 在trigger分析任务时产生
    "time": "2018-04-02 14:00:00",
    // 截取视频流的时间
    "success": true,
    // 任务是否成功进行
    "data": {
      // 机器存在分析结果
      "confidence": 0.94,
      // 机器在的概率
      "toolExists": true,
      // 机器在的结论， 平台也可以根据概率自行得出结论
      "prof": "base64:xxxxxxxxxxxxx"
      // base64编码jpg图像， 为捕捉改机器的图片
    }
  },
  //  Exchange: alarm.equipment.move
  //Queue: alarm.equipment.move
  //routingKey: alarm.equipment.move.#


  {
    "deviceId": 12346,
    // 摄像头id
    "taskId": 12346,
    // 在trigger分析任务时产生
    "time": "2018-04-02 14:00:00",
    // 截取视频流的时间
    "success": true,
    // 任务是否成功进行
    "data": {
      // 机器存在分析结果
      "confidence": 0.94,
      // 机器在的概率
      "toolExists": true,
      // 机器在的结论， 平台也可以根据概率自行得出结论
      "prof": "base64:xxxxxxxxxxxxx"
      // base64编码jpg图像， 为捕捉改机器的图片
    }
  },
  //  Exchange: alarm.equipment.work
  //Queue: alarm.equipment.work
  //routingKey: alarm.equipment.work.#


  {
    "deviceId": 12346,
    // 摄像头id
    "taskId": 12345,
    // 在trigger分析任务时产生
    "time": "2018-04-02 14:00:00",
    // 截取视频流的时间
    "success": true,
    // 任务是否成功进行
    "data": [
      //人脸识别结果
      {
        "eid": "H232559",
        // 工号
        "confidence": 0.76,
        // 该工人出现过的评分，一般高于0.5认为出现过
        "prof": "base64:xxxxxxxxxxxxx"
        // base64编码jpg图像，为疑似该工人出现过的图像
      },
      {
        "eid": "H123456",
        "confidence": 0.1,
        "prof": "base64:xxxxxxxxxxxxx"
      },
      {
        "eid": "H456789",
        "confidence": 0.0,
        "prof": "base64:xxxxxxxxxxxxx"
      }
    ]
  }

  //  Exchange: alarm.worker.diff
  //Queue: alarm.worker.diff
  //routingKey: alarm.worker.diff.#
];



