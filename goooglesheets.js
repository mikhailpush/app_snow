function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = (e && e.parameter && e.parameter.sheet) ? e.parameter.sheet : "Sheet1";
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }
  var rows = sheet.getDataRange().getValues();
  return ContentService.createTextOutput(JSON.stringify(rows))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
    var d = JSON.parse(e.postData.contents);

    if (d.action === "clear") {
      var lastRow = sheet.getLastRow();
      if (lastRow > 1) {
        sheet.deleteRows(2, lastRow - 1);
      }
      return ContentService.createTextOutput(JSON.stringify({"status": "cleared"}))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // Серверная проверка дубликатов по Фамилии + Имени + Классу
    var data = sheet.getDataRange().getValues();
    var targetLast = String(d.LastName || "").trim().toLowerCase();
    var targetFirst = String(d.FirstName || "").trim().toLowerCase();
    var targetGrade = String(d.Grade || "").trim().toLowerCase();

    for (var i = 1; i < data.length; i++) {
      var rLast = String(data[i][1] || "").trim().toLowerCase();
      var rFirst = String(data[i][2] || "").trim().toLowerCase();
      var rGrade = String(data[i][3] || "").trim().toLowerCase();
      if (rLast === targetLast && rFirst === targetFirst && rGrade === targetGrade) {
        return ContentService.createTextOutput(JSON.stringify({"status": "duplicate_ignored"}))
          .setMimeType(ContentService.MimeType.JSON);
      }
    }

    sheet.appendRow([
      d.Timestamp,
      d.LastName,
      d.FirstName,
      d.Grade,
      d.League,
      d.Codename,
      d.Score,
      d.TimeSec,
      d.Details
    ]);
    return ContentService.createTextOutput(JSON.stringify({"status": "ok"}))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
