const database = require("../database/database");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const nodemailer = require("nodemailer");
require("dotenv").config();

// 기존 PostAuthCtrl.js의 함수들
exports.postAuth = async (request, response) => {
  const { email, password, birth_date } = request.body;

  try {
    const result = await database.pool.query(
      "SELECT * FROM Auth WHERE email = $1",
      [email]
    );

    if (result.rows.length > 0) {
      return response
        .status(200)
        .json({ msg: "이미 존재하는 이메일 입니다.", success: false });
    }

    const hashPassword = await bcrypt.hash(password, 10);

    await database.pool.query(
      "INSERT INTO Auth (email, password, birth_date) VALUES ($1, $2, $3)",
      [email, hashPassword, birth_date]
    );

    return response
      .status(200)
      .json({ msg: "회원가입이 완료되었습니다.", success: true });
  } catch (error) {
    console.error("회원가입 중 오류 발생:", error);
    return response.status(500).json({ msg: "회원정보 입력 오류: " + error });
  }
};

// UpdateAuthCtrl.js의 함수를 updateUser로 변경
exports.updateUser = async (request, response) => {
  const { email, password } = request.body;

  try {
    const hashPassword = await bcrypt.hash(password, 10);

    await database.pool.query(
      "UPDATE Auth SET password = $1 WHERE email = $2",
      [hashPassword, email]
    );

    return response.status(200).json({ msg: "회원정보가 수정되었습니다." });
  } catch (error) {
    return response.status(500).json({ msg: "데이터 입력 에러: ", error });
  }
};

// DeleteAuthCtrl.js의 함수를 deleteUser로 변경
exports.deleteUser = async (request, response) => {
  const userID = request.params.id;

  if (!userID) {
    return response.status(400).json({ msg: "잘못된 요청입니다." });
  }

  try {
    const result = await database.pool.query(
      "DELETE FROM Auth WHERE user_id = $1",
      [userID]
    );

    if (result.rowCount === 0) {
      return response.status(404).json({ msg: "회원정보가 없습니다." });
    }

    return response.status(200).json({ msg: "회원정보 삭제 성공" });
  } catch (error) {
    return response.status(500).json({
      msg: "회원정보 삭제 실패",
      error: error.message,
    });
  }
};

// emailCtrl.js의 함수를 sendEmail로 변경
exports.sendEmail = async (req, res) => {
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
    return res.status(500).json({
      success: false,
      message: "이메일 전송에 실패했습니다.",
      error: error.message,
    });
  }
};

exports.postLogin = async (request, response) => {
  const { email, password } = request.body;
  try {
    const result = await database.pool.query(
      "SELECT * FROM Auth WHERE email = $1",
      [email]
    );

    if (result.rows.length === 0) {
      return response.status(401).json({
        msg: "이메일 또는 비밀번호가 일치하지 않습니다.",
        success: false,
      });
    }

    const user = result.rows[0];
    const isValidPassword = await bcrypt.compare(password, user.password);

    if (!isValidPassword) {
      return response.status(401).json({
        msg: "이메일 또는 비밀번호가 일치하지 않습니다.",
        success: false,
      });
    }

    const token = jwt.sign(
      { id: user.user_id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: "24h" }
    );

    return response.status(201).json({
      msg: "로그인 성공",
      success: true,
      token: token,
      data: {
        user_id: user.user_id,
        email: user.email,
      },
    });
  } catch (error) {
    return response.status(500).json({
      msg: "로그인 오류",
      error: error.message,
    });
  }
};

exports.sendEmailVerification = async (request, response) => {
  console.log("이메일 인증 요청 수신:", request.body);
  const { email } = request.body;

  try {
    // 인증 코드 생성 (6자리)
    const verificationCode = Math.floor(
      100000 + Math.random() * 900000
    ).toString();

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
      to: email,
      subject: "[SmartFarm] 이메일 인증 코드",
      text: `인증 코드: ${verificationCode}\n\n이 코드는 10분간 유효합니다.`,
    };

    await transporter.sendMail(mailOptions);

    return response.status(200).json({
      success: true,
      message: "인증 코드가 발송되었습니다.",
      data: { verificationCode },
    });
  } catch (error) {
    console.error("이메일 인증 코드 발송 실패:", error);
    return response.status(500).json({
      success: false,
      message: "인증 코드 발송에 실패했습니다.",
      error: error.message,
    });
  }
};

exports.findPwd = async (request, response) => {
  // 비밀번호 찾기 로직 구현
};

exports.resetPwd = async (request, response) => {
  // 비밀번호 재설정 로직 구현
};

exports.getUserInfo = async (req, res) => {
  const userId = req.user.id; // JWT 토큰에서 사용자 ID를 가져온다고 가정

  try {
    const result = await database.pool.query(
      "SELECT email, user_id, created_at FROM Auth WHERE user_id = $1",
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ msg: "사용자 정보를 찾을 수 없습니다." });
    }

    return res.status(200).json(result.rows[0]);
  } catch (error) {
    return res
      .status(500)
      .json({ msg: "사용자 정보 로드 실패", error: error.message });
  }
};

module.exports = {
  postAuth: exports.postAuth,
  postLogin: exports.postLogin,
  sendEmailVerification: exports.sendEmailVerification,
  findPwd: exports.findPwd,
  resetPwd: exports.resetPwd,
  updateUser: exports.updateUser,
  deleteUser: exports.deleteUser,
  sendEmail: exports.sendEmail,
  getUserInfo: exports.getUserInfo,
};
