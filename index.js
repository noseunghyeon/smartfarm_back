const express = require("express");
const cors = require("cors");
const path = require("path");
const spawn = require("child_process").spawn;
const { pool } = require("./database/database");
const authRoutes = require("./routes/authRoutes");
const { authenticateToken } = require("./utils/authenticate");
const weatherRoutes = require("./routes/weatherRoutes");

require("dotenv").config();
const postgresqlRouters = require("./routes/postgresqlRouters");
const emailRouter = require("./routes/emailRouter");
const writeRouter = require("./routes/writeRouter");
const commentsRouter = require("./routes/commentsRoutes");

let fastApiProcess = null; // FastAPI 프로세스 저장용 변수

// FastAPI 서버 시작 함수
function startFastApiServer() {
  console.log("Starting FastAPI server...");

  // Python 가상환경이 있는 경우 해당 경로 사용
  const pythonPath = "python"; // 또는 'python3'

  fastApiProcess = spawn(pythonPath, [
    "-m",
    "uvicorn",
    "app:app",
    "--reload",
    "--port",
    "8000",
  ]);

  fastApiProcess.stdout.on("data", (data) => {
    console.log(`FastAPI: ${data}`);
  });

  fastApiProcess.stderr.on("data", (data) => {
    console.error(`FastAPI Error: ${data}`);
  });

  fastApiProcess.on("close", (code) => {
    console.log(`FastAPI process exited with code ${code}`);
  });
}

// Express 서버는 9000 포트 사용
const PORT = 9000;

// Express 서버 설정
const app = express();

// CORS 설정
app.use(
  cors({
    origin: "http://localhost:3000", // 프론트엔드의 URL
    methods: ["GET", "POST", "PUT", "DELETE"], // 허용할 HTTP 메서드
    credentials: true, // 쿠키와 같은 인증 정보를 포함할지 여부
  })
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use("/api/comments", commentsRouter);

// 데이터베이스 연결 테스트
app.get("/api/test-db", async (req, res) => {
  try {
    const result = await pool.query("SELECT NOW()");
    res.json({ success: true, timestamp: result.rows[0].now });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 판매 데이터 조회 API
app.get("/api/sales", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM sales_data_2024");
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// TOP 10 데이터 조회 API
app.get("/api/top10", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM top_10_sales");
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 루트 경로 호출
app.get("/", (request, response) => {
  console.log(`Server is running on port ${PORT}`);
  response.send("Server is running");
});

const pythonExePath = path.join("python");

app.post("/get_text", (req, res) => {
  try {
    const scriptPath = path.join(__dirname, "app.py");
    const pythonProcess = spawn(pythonExePath, [scriptPath]);

    // Python 스크립트로 데이터 전송
    pythonProcess.stdin.write(JSON.stringify(req.body));
    pythonProcess.stdin.end();

    let result = "";

    // Python 스크립트로부터 결과 받기
    pythonProcess.stdout.on("data", (data) => {
      result += data.toString();
    });

    // 에러 처리
    pythonProcess.stderr.on("data", (data) => {
      console.error(`Python Error: ${data}`);
    });

    // 프로세스 종료 시
    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        return res.status(500).json({
          success: false,
          error: "Python process failed",
        });
      }
      try {
        const prediction = JSON.parse(result);
        res.json(prediction);
      } catch (error) {
        res.status(500).json({
          success: false,
          error: "Failed to parse Python output",
        });
      }
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message,
    });
  }
});

// 라우트 설정
app.use("/api", postgresqlRouters);
app.use("/auth", authRoutes);
app.use("/api", emailRouter);
app.use("/", weatherRoutes);
app.use("/api/write", writeRouter);

// Express 서버 시작
app.listen(PORT, () => {
  console.log(`Express server is running on port ${PORT}`);
  // Express 서버가 시작된 후 FastAPI 서버 시작
  startFastApiServer();
});

// 프로세스 종료 시 정리
process.on("SIGINT", () => {
  // FastAPI 서버 종료
  if (fastApiProcess) {
    console.log("Shutting down FastAPI server...");
    fastApiProcess.kill();
  }

  // PostgreSQL pool 정리
  pool.end(() => {
    console.log("Pool has ended");
    process.exit(0);
  });
});
