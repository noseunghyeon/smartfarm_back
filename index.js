const express = require("express");
const cors = require("cors");
const path = require("path");
const spawn = require("child_process").spawn;
const { pool } = require("./database/database");

require("dotenv").config();
const postgresqlRouters = require("./routes/postgresqlRouters");
const authRoutes = require("./routes/authRoutes");
const emailRouter = require("./routes/emailRouter");

const app = express();
const PORT = 8000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// 프로세스 종료 시 Pool 정리
process.on("SIGINT", () => {
  pool.end(() => {
    console.log("Pool has ended");
    process.exit(0);
  });
});
