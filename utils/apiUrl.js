// 외부 API 기본 URL 설정
const BASE_URL = "https://api.example.com";

// API 요청 함수 예시
async function fetchData(endpoint) {
  const response = await fetch(`${BASE_URL}/${endpoint}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

module.exports = {
  BASE_URL,
  fetchData,
};
