const express = require("express");
const cors = require("cors");
const path = require("path");
const spawn = require("child_process").spawn;
const app = express();

const PORT = 8000;

app.use(cors());
app.use(express.json());

// 루트 경로 호출
app.get("/", (request, response) => {
  console.log(`Server is running on port ${PORT}`);
  response.send("Server is running");
});

const pythonExePath = path.join("python");

app.get("/get_text", (request, response) => {
  const scriptPath = path.join(__dirname, "app.py");
  const result = spawn(pythonExePath, [scriptPath]);

  let resData = "";

  result.stdout.on("data", (data) => {
    resData += data.toString();
  });

  result.on("close", (code) => {
    if (code === 0) {
      // const jsonData = JSON.parse(resData);
      response.json(resData);
    } else {
      response
        .status(500)
        .json({ error: `Child process exited with code ${code}` });
    }
  });
});

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

// 서버 실행
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
