const database = require("../database/database");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

const nodemailer = require("nodemailer");
require("dotenv").config();

exports.postAuth = async (request, response) => {
  const { email, password, birth_date } = request.body;

  console.log(email, password, birth_date); // body에 들어온 값 확인

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

    // 비밀번호 해싱
    const hashPassword = await bcrypt.hash(password, 10);
    console.log(hashPassword);

    // 사용자 정보 DB에 저장
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

exports.sendEmailVerification = async (request, response) => {
  const { email } = request.body;

  try {
    // 이메일 발송을 위한 Nodemailer 설정
    const transporter = nodemailer.createTransport({
      host: "smtp.naver.com",
      port: 465,
      secure: true,
      auth: {
        user: process.env.EMAIL,
        pass: process.env.EMAIL_PASSWORD,
      },
    });

    // 이메일 인증 코드 생성 함수
    const generateCode = () => {
      const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
      let code = "";
      for (let i = 0; i < 6; i++) {
        code += characters.charAt(
          Math.floor(Math.random() * characters.length)
        );
      }
      return code;
    };

    // 인증 코드 생성
    const verificationCode = generateCode();

    // 이메일 발송
    const mailOptions = {
      from: process.env.EMAIL,
      to: email,
      subject: "이메일 인증 코드",
      text: `회원가입을 위한 인증 코드는 ${verificationCode} 입니다.`,
    };

    // 이메일 발송
    await transporter.sendMail(mailOptions);

    return response.status(200).json({
      success: true,
      message: "인증 코드가 이메일로 전송되었습니다.",
      verificationCode: verificationCode,
    });
  } catch (error) {
    console.error("이메일 발송 실패:", error);
    return response.status(500).json({
      success: false,
      message: "이메일 발송에 실패했습니다.",
      error: error.message,
    });
  }
};

exports.postLogin = async (request, response) => {
  const { email, password } = request.body;

  try {
    console.log("JWT_SECRET:", process.env.JWT_SECRET);

    const result = await database.pool.query(
      "SELECT * FROM Auth WHERE email = $1",
      [email]
    );

    if (result.rows.length === 0) {
      return response
        .status(200)
        .json({ msg: "존재하지 않는 사용자 입니다.", success: false });
    }

    // 2. 비밀빈호 복호화, 비밀번호 일치 여부 확인
    const isMatch = await bcrypt.compare(password, result.rows[0].password);
    // 첫번째 파라미터는 입력 받은 비밀번호, 두번째 파라미터는 데이터베이스에 있는 암호화된 비밀번호 - 비교해서 맞으면 true, 틀리면 false

    if (!isMatch) {
      // 비밀번호가 틀린경우
      return response
        .status(200)
        .json({ msg: "비밀번호가 일치하지 않습니다.", success: false });
    }

    // 3. 회원정보 jsonwebtoken 생성
    // sign 함수: 첫번째 파라미터는 결과값, 두번째 파라미터는 시크릿키, 세번째 파라미터는 유효기간
    const token = jwt.sign(
      {
        id: result.rows[0].id,
        email: result.rows[0].email,
      },
      process.env.JWT_SECRET,
      { expiresIn: "3h" }
    );

    return response.status(201).json({ token, msg: "로그인 성공" });
  } catch (error) {
    return response.status(500).json({ msg: "로그인 실패: " + error });
  }
}; // postLogin 함수 끝

exports.findPwd = async (req, res) => {
  const { email } = req.body;

  try {
    // 사용자 존재 여부 확인
    const result = await database.pool.query(
      "SELECT * FROM Auth WHERE email = $1",
      [email]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "사용자를 찾을 수 없습니다." });
    }

    // 비밀번호 재설정 토큰 생성
    const token = jwt.sign(
      { userId: result.rows[0].id },
      process.env.JWT_SECRET,
      { expiresIn: "1h" }
    );

    // 이메일 전송 설정
    const transporter = nodemailer.createTransport({
      host: "smtp.naver.com",
      port: 465,
      secure: true,
      auth: {
        user: process.env.EMAIL,
        pass: process.env.EMAIL_PASSWORD,
      },
    });

    const resetUrl = `http://localhost:3000/resetpwd?token=${token}`;

    const mailOptions = {
      from: process.env.EMAIL,
      to: email,
      subject: "비밀번호 재설정",
      html: `
        <h1>비밀번호 재설정</h1>
        <p>아래 링크를 클릭하여 비밀번호를 재설정하세요:</p>
        <a href="${resetUrl}">비밀번호 재설정하기</a>
        <p>이 링크는 1시간 동안만 유효합니다.</p>
      `,
    };

    await transporter.sendMail(mailOptions);
    return res.json({ message: "비밀번호 재설정 이메일을 발송했습니다." });
  } catch (error) {
    return res
      .status(500)
      .json({ error: "이메일 발송 실패: " + error.message });
  }
};

exports.resetPwd = async (req, res) => {
  const { token, newPassword } = req.body;

  try {
    // 토큰 검증
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    const hashedPassword = await bcrypt.hash(newPassword, 10);

    // DB에서 비밀번호 업데이트
    await database.pool.query("UPDATE Auth SET password = $1 WHERE id = $2", [
      hashedPassword,
      decoded.userId,
    ]);

    return res.json({ message: "비밀번호가 성공적으로 변경되었습니다." });
  } catch (error) {
    if (error.name === "JsonWebTokenError") {
      return res
        .status(401)
        .json({ error: "유효하지 않거나 만료된 토큰입니다." });
    }
    return res
      .status(500)
      .json({ error: "비밀번호 재설정 실패: " + error.message });
  }
};
