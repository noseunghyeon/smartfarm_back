const database = require("../database/database");

exports.deleteAuth = async (request, response) => {
  const userID = request.params.id;

  if (!userID) {
    return response.status(400).json({ msg: "잘못된 요청입니다." });
  }

  try {
    const result = await database.pool.query("DELETE FROM Auth WHERE id = $1", [
      userID,
    ]);

    if (result.rowCount === 0) {
      return response.status(404).json({ msg: "회원정보가 없습니다." });
    }

    return response.status(200).json({ msg: "회원정보 삭제 성공" });
  } catch (error) {
    return response
      .status(500)
      .json({ msg: "회원정보 삭제 실패", error: error.message });
  }
};
