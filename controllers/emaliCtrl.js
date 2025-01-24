const nodemailer = require("nodemailer");
const cron = require("node-cron");
require("dotenv").config();
const database = require("../database/database");

exports.emailCtrl = async (req, res) => {
  const { title, content, email, category } = req.body;

  if (!email) {
    return res.status(400).json({
      success: false,
      message: "이메일 주소가 필요합니다.",
    });
  }

  const transporter = nodemailer.createTransport({
    host: "smtp.naver.com",
    port: 465,
    secure: true,
    auth: {
      user: process.env.EMAIL,
      pass: process.env.EMAIL_PASSWORD,
    },
  });

  const mailOptions = {
    from: process.env.EMAIL,
    to: process.env.EMAIL,
    subject: `[건의사항] ${category} - ${title}`,
    text: `
카테고리: ${category}
제목: ${title}
내용: ${content}
수신받을 이메일: ${email}

이 메일은 자동발송됩니다.
    `,
  };

  try {
    await transporter.sendMail(mailOptions);
    return res.status(200).json({
      success: true,
      message: "건의사항이 성공적으로 전송되었습니다.",
    });
  } catch (error) {
    console.error("이메일 전송 실패:", error);
    console.error("자세한 에러:", error.message);
    return res.status(500).json({
      success: false,
      message: "이메일 전송에 실패했습니다.",
      error: error.message,
    });
  }
};

// 9시에 실행되는 cron job
cron.schedule("0 9 * * *", async () => {
  try {
    // 유효기간 7일 전인 약품과 사용자 정보 조회
    const { rows: notifications } = await database.pool.query(` 
      SELECT
        m.id AS mediId,
        m.medi_name AS mediName,
        m.exp_date AS expDate,
        u.email AS userEmail
      FROM mymedicine m
      JOIN users u ON m.user_id = u.id
      WHERE
        m.exp_date::date = CURRENT_DATE + INTERVAL '7 days'
        AND m.notification = true
    `);

    // 디버깅을 위한 로그 추가
    console.log("조회된 알림 대상:", notifications);

    for (const notification of notifications) {
      try {
        await sendNotificationEmail(notification);

        // 알림 발송 기록
        await database.pool.query(
          `
          INSERT INTO notification_logs
          (medicine_id, sent_date, status)
          VALUES ($1, NOW(), 'sent')
        `,
          [notification.mediid]
        );
      } catch (error) {
        console.error(
          `알림 발송 실패 (약품 ID: ${notification.mediid}):`,
          error
        );

        // 실패 로그 기록
        await database.pool.query(
          `
          INSERT INTO notification_logs
          (medicine_id, sent_date, status, error_message)
          VALUES ($1, NOW(), 'failed', $2)
        `,
          [notification.mediId, error.message]
        );
      }
    }
  } catch (error) {
    console.error("알림 처리 중 오류 발생:", error);

    // 오류 로그 기록
    await database.pool.query(
      `
      INSERT INTO error_logs
      (error_message, error_date, stack_trace)
      VALUES ($1, NOW(), $2)
    `,
      [error.message, error.stack]
    );
  }
});

async function sendNotificationEmail(notification) {
  const transporter = nodemailer.createTransport({
    host: "smtp.naver.com",
    port: 465,
    secure: true,
    auth: {
      user: process.env.EMAIL,
      pass: process.env.EMAIL_PASSWORD,
    },
  });

  const mailOptions = {
    from: process.env.EMAIL,
    to: notification.useremail,
    subject: `[알림] ${notification.mediname} 유효기간이 7일 남았습니다`,
    text: `
안녕하세요.
등록하신 의약품 "${
      notification.mediname
    }"의 유효기간이 7일 남았음을 알려드립니다.

- 의약품명: ${notification.mediname}
- 유효기간: ${new Date(notification.expdate).toLocaleDateString()}

안전한 의약품 사용을 위해 유효기간을 확인해주세요.

이 메일은 자동발송됩니다.
    `,
  };

  await transporter.sendMail(mailOptions);
}
