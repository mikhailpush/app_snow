// Вспомогательная функция для нормализации ФИО и класса при сверке дублей
function normalizeStr(val) {
  return String(val || "")
    .trim()
    .toLowerCase()
    .replace(/ё/g, "е");
}

// Автоматическая проверка и создание шапки таблицы, если лист пуст
function ensureHeaders(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "Timestamp",
      "LastName",
      "FirstName",
      "Grade",
      "League",
      "Codename",
      "Score",
      "TimeSec",
      "Details"
    ]);
  }
}

// Чтение результатов (Sheet1) или кастомного банка вопросов (Questions)
function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = (e && e.parameter && e.parameter.sheet) ? e.parameter.sheet : "Sheet1";
  var sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  if (sheetName === "Sheet1") {
    ensureHeaders(sheet);
  }

  var rows = sheet.getDataRange().getDisplayValues();
  return ContentService.createTextOutput(JSON.stringify(rows))
    .setMimeType(ContentService.MimeType.JSON);
}

// Запись новых результатов и очистка базы с защитой от гонки потоков
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000); // Очередь до 10 секунд при одновременном финише класса

  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Sheet1");
    if (!sheet) {
      sheet = ss.insertSheet("Sheet1");
    }
    ensureHeaders(sheet);

    var d = JSON.parse(e.postData.contents);

    // 1. Команда очистки пробных попыток из панели учителя
    if (d.action === "clear") {
      var lastRow = sheet.getLastRow();
      if (lastRow > 1) {
        sheet.deleteRows(2, lastRow - 1);
      }
      return ContentService.createTextOutput(JSON.stringify({"status": "cleared"}))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // 2. Серверная защита от дублей (защита от отправки из нескольких вкладок)
    var data = sheet.getDataRange().getValues();
    var targetLast = normalizeStr(d.LastName);
    var targetFirst = normalizeStr(d.FirstName);
    var targetGrade = normalizeStr(d.Grade);

    for (var i = 1; i < data.length; i++) {
      if (
        normalizeStr(data[i][1]) === targetLast &&
        normalizeStr(data[i][2]) === targetFirst &&
        normalizeStr(data[i][3]) === targetGrade
      ) {
        return ContentService.createTextOutput(
          JSON.stringify({
            "status": "duplicate",
            "codename": data[i][5],
            "score": data[i][6]
          })
        ).setMimeType(ContentService.MimeType.JSON);
      }
    }

    // 3. Запись результата нового участника
    sheet.appendRow([
      d.Timestamp || new Date().toISOString(),
      d.LastName,
      d.FirstName,
      d.Grade,
      d.League,
      d.Codename,
      Number(d.Score) || 0,
      Number(d.TimeSec) || 0,
      d.Details || ""
    ]);

    return ContentService.createTextOutput(JSON.stringify({"status": "ok"}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({"status": "error", "message": String(err)})
    ).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
