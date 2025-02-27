const database = require("../database/database");

const writeCtrl = {
  // 게시글 생성
  create: async (req, res) => {
    try {
      const { title, content, category, community_type } = req.body;
      const user_id = req.user.id; // authenticateToken에서 설정한 user 정보

      const result = await database.pool.query(
        "INSERT INTO write (user_id, title, content, category, community_type, date) VALUES ($1, $2, $3, $4, $5, CURRENT_DATE) RETURNING *",
        [user_id, title, content, category, community_type]
      );

      res.status(201).json({
        success: true,
        message: "게시글이 생성되었습니다.",
        data: result.rows[0],
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({
        success: false,
        message: "게시글 작성 실패",
        error: err.message,
      });
    }
  },

  // 모든 게시글 조회
  getPosts: async (req, res) => {
    try {
      const result = await database.pool.query(
        "SELECT w.*, a.email FROM write w JOIN Auth a ON w.user_id = a.user_id ORDER BY date DESC"
      );

      res.status(200).json({
        success: true,
        data: result.rows,
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({
        success: false,
        message: "게시글 조회 실패",
        error: err.message,
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
        return res.status(404).json({
          success: false,
          message: "게시글을 찾을 수 없습니다.",
        });
      }

      res.status(200).json({
        success: true,
        data: result.rows[0],
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({
        success: false,
        message: "게시글 조회 실패",
        error: err.message,
      });
    }
  },

  // 특정 커뮤니티의 게시글 조회 추가
  getPostsByType: async (req, res) => {
    try {
      const { type } = req.params; // gardening, marketplace, freeboard

      const result = await database.pool.query(
        "SELECT w.*, a.email FROM write w JOIN Auth a ON w.user_id = a.user_id WHERE w.community_type = $1 ORDER BY date DESC",
        [type]
      );

      res.status(200).json({
        success: true,
        data: result.rows,
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({
        success: false,
        message: "게시글 조회 실패",
        error: err.message,
      });
    }
  },

  // 게시글 수정
  updatePost: async (req, res) => {
    try {
      const { id } = req.params;
      const { title, content, category, community_type } = req.body;
      const user_id = req.user.id;

      // 게시글 작성자 확인
      const checkResult = await database.pool.query(
        "SELECT user_id FROM write WHERE post_id = $1",
        [id]
      );

      if (checkResult.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: "게시글을 찾을 수 없습니다.",
        });
      }

      if (checkResult.rows[0].user_id !== user_id) {
        return res.status(403).json({
          success: false,
          message: "게시글을 수정할 권한이 없습니다.",
        });
      }

      const result = await database.pool.query(
        "UPDATE write SET title = $1, content = $2, category = $3, community_type = $4, date = CURRENT_DATE WHERE post_id = $5 RETURNING *",
        [title, content, category, community_type, id]
      );

      res.status(200).json({
        success: true,
        message: "게시글이 수정되었습니다.",
        data: result.rows[0],
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({
        success: false,
        message: "게시글 수정 실패",
        error: err.message,
      });
    }
  },

  // 게시글 삭제
  deletePost: async (req, res) => {
    try {
      const { id } = req.params;
      const user_id = req.user.id;

      // 게시글 작성자 확인
      const checkResult = await database.pool.query(
        "SELECT user_id FROM write WHERE post_id = $1",
        [id]
      );

      if (checkResult.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: "게시글을 찾을 수 없습니다.",
        });
      }

      if (checkResult.rows[0].user_id !== user_id) {
        return res.status(403).json({
          success: false,
          message: "게시글을 삭제할 권한이 없습니다.",
        });
      }

      await database.pool.query("DELETE FROM write WHERE post_id = $1", [id]);

      res.status(200).json({
        success: true,
        message: "게시글이 삭제되었습니다.",
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({
        success: false,
        message: "게시글 삭제 실패",
        error: err.message,
      });
    }
  },
};

module.exports = { writeCtrl };
