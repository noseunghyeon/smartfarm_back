const database = require("../database/database");

const writeCtrl = {
  // 게시글 생성
  create: async (req, res) => {
    try {
      const { user_id, title, name, content } = req.body;
      const result = await database.pool.query(
        "INSERT INTO write (user_id, title, name, content) VALUES ($1, $2, $3, $4) RETURNING *",
        [user_id, title, name, content]
      );
      res.status(201).json({ success: true, data: result.rows[0] });
    } catch (error) {
      res
        .status(500)
        .json({
          success: false,
          message: "게시글 작성 실패",
          error: error.message,
        });
    }
  },

  // 모든 게시글 조회
  getPosts: async (req, res) => {
    try {
      const result = await database.pool.query(
        "SELECT w.*, a.email FROM write w JOIN Auth a ON w.user_id = a.user_id ORDER BY date DESC"
      );
      res.status(200).json({ success: true, data: result.rows });
    } catch (error) {
      res
        .status(500)
        .json({
          success: false,
          message: "게시글 조회 실패",
          error: error.message,
        });
    }
  },

  // 특정 게시글 조회
  getPost: async (req, res) => {
    try {
      const { id } = req.params;
      const result = await database.pool.query(
        "SELECT w.*, a.email FROM write w JOIN Auth a ON w.user_id = a.user_id WHERE post_id = $1",
        [id]
      );

      if (result.rows.length === 0) {
        return res
          .status(404)
          .json({ success: false, message: "게시글을 찾을 수 없습니다." });
      }

      res.status(200).json({ success: true, data: result.rows[0] });
    } catch (error) {
      res
        .status(500)
        .json({
          success: false,
          message: "게시글 조회 실패",
          error: error.message,
        });
    }
  },

  // 게시글 수정
  updatePost: async (req, res) => {
    try {
      const { id } = req.params;
      const { title, content } = req.body;
      const result = await database.pool.query(
        "UPDATE write SET title = $1, content = $2, date = CURRENT_DATE WHERE post_id = $3 RETURNING *",
        [title, content, id]
      );

      if (result.rows.length === 0) {
        return res
          .status(404)
          .json({ success: false, message: "게시글을 찾을 수 없습니다." });
      }

      res.status(200).json({ success: true, data: result.rows[0] });
    } catch (error) {
      res
        .status(500)
        .json({
          success: false,
          message: "게시글 수정 실패",
          error: error.message,
        });
    }
  },

  // 게시글 삭제
  deletePost: async (req, res) => {
    try {
      const { id } = req.params;
      const result = await database.pool.query(
        "DELETE FROM write WHERE post_id = $1 RETURNING *",
        [id]
      );

      if (result.rows.length === 0) {
        return res
          .status(404)
          .json({ success: false, message: "게시글을 찾을 수 없습니다." });
      }

      res
        .status(200)
        .json({ success: true, message: "게시글이 삭제되었습니다." });
    } catch (error) {
      res
        .status(500)
        .json({
          success: false,
          message: "게시글 삭제 실패",
          error: error.message,
        });
    }
  },
};

module.exports = { writeCtrl };
