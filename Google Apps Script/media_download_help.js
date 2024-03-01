
function extractHashFromMagnet(magnetUrl) {
  var match = magnetUrl.match(/urn:btih:([a-zA-Z0-9]+)/);
  return match ? match[1] : null;
}

function sendMessageToBot(text, chat_id) {
  var payload = {
    "method": "sendMessage",
    "chat_id": chat_id,
    "text": text
  }
  var post_data = {
    "method": "post",
    "payload": payload
  }
  UrlFetchApp.fetch("https://api.telegram.org/bot<将 Telegram Bot TOKEN 填充到此处, 删除尖括号>/", post_data);
  // 例如 TOKEN = 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
  // UrlFetchApp.fetch("https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/", post_data);
}

function doGet(e) {
  var data = [];
  var lock = LockService.getScriptLock();
  if (lock.tryLock(5000)) {
    try {
      const scriptProperties = PropertiesService.getScriptProperties();
      const prop_data = scriptProperties.getProperties();
      for (const key in prop_data) {
        // console.log('Key: %s, Value: %s', key, data[key]);
        data.push({hash: key, magnet: prop_data[key]});
        scriptProperties.deleteProperty(key);
      }
    } catch (err) {
      console.log('Failed with error %s', err.message);
    } finally {
      lock.releaseLock();
    }
  }
  var payload_data = {
    'status': 'OK',
    'magnet_urls': data
  }
  return ContentService.createTextOutput(JSON.stringify(payload_data))
    .setMimeType(ContentService.MimeType.JSON);
}



function doPost(e) {
  var body = JSON.parse(e.postData.contents);
  var hash_key = extractHashFromMagnet(body.message.text)

  if (hash_key == null) {
    sendMessageToBot("Magnet Url 格式错误, 无法获取到 hash 值!", body.message.chat.id.toString());
    return;
  }

  var value = {
    'chat_id': body.message.chat.id,
    'url': body.message.text
  }

  var lock = LockService.getScriptLock();
  if (lock.tryLock(5000)) {
    try {
      const scriptProperties = PropertiesService.getScriptProperties();
      var repeatdata = scriptProperties.getProperty(hash_key);
      if (repeatdata != null) {
        sendMessageToBot("Magnet Url 已存在, 请勿重复添加!", body.message.chat.id.toString());
      } else {
        scriptProperties.setProperty(hash_key, JSON.stringify(value));
        sendMessageToBot("Magnet Url 添加成功, 等待下载!", body.message.chat.id.toString());
      }

    } catch (err) {
      console.log('Failed with error %s', err.message);
      sendMessageToBot("Magnet Url 添加失败, 请稍后重试!", body.message.chat.id.toString());
    } finally {
      lock.releaseLock();
    }
  } else {
    sendMessageToBot("Magnet Url 添加失败, 请稍后重试!", body.message.chat.id.toString());
  }
}

