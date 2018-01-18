# токен бота
token = "469439337:AAFf3jESyXKNcT3Fj7dePlRMZ8yR87TjUls"
# информация о БД
host = 'sql11.freemysqlhosting.net'
user = 'sql11211944'
password = 'ivsEhZGkgX'
port = 3306
# запрос для БД
sql = """SELECT `sql11211944`.SubmitResult.ID, `sql11211944`.SubmitResult.ResultTime,
    `sql11211944`.AcmSubmitDisplayResult.`Status`
    FROM `sql11211944`.AcmSubmitDisplayResult
    INNER JOIN `sql11211944`.SubmitResult
    ON `sql11211944`.AcmSubmitDisplayResult.ID = `sql11211944`.SubmitResult.AcmDisplayResult_id
    WHERE STATUS LIKE "ServerError"
    OR STATUS LIKE "Pending"
    ORDER BY `sql11211944`.SubmitResult.ID
    DESC LIMIT 50"""
# количество секунд между отправками
interval = 15