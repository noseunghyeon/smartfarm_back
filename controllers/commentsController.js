const { pool } = require("../database/database");

const commentsController = {
  // 게시글의 모든 댓글 조회
  getComments: async (req, res) => {
    try {
      const comments = await pool.query(
        `SELECT c.*, a.email 
                 FROM comments c 
                 JOIN auth a ON c.user_id = a.user_id 
                 WHERE c.post_id = $1 
                 ORDER BY c.created_at DESC`,
        [req.params.postId]
      );
      res.json(comments.rows);
    } catch (error) {
      console.error("댓글 조회 오류:", error);
      res.status(500).json({ message: "댓글을 불러오는데 실패했습니다." });
    }
  },

  // 새 댓글 작성
  createComment: async (req, res) => {
    const { post_id, content } = req.body;
    const user_id = req.user.id; // JWT 토큰에서 추출된 사용자 ID

    try {
      // 게시글 존재 여부 확인
      const postCheck = await pool.query(
        "SELECT * FROM write WHERE post_id = $1",
        [post_id]
      );

      if (postCheck.rows.length === 0) {
        return res.status(404).json({
          message: "해당 게시글이 존재하지 않습니다.",
        });
      }

      const newComment = await pool.query(
        `INSERT INTO comments (post_id, user_id, content) 
                 VALUES ($1, $2, $3) 
                 RETURNING *`,
        [post_id, user_id, content]
      );

      // 이메일 정보를 포함하여 반환
      const commentWithEmail = await pool.query(
        `SELECT c.*, a.email 
                 FROM comments c 
                 JOIN auth a ON c.user_id = a.user_id 
                 WHERE c.comment_id = $1`,
        [newComment.rows[0].comment_id]
      );

      res.status(201).json(commentWithEmail.rows[0]);
    } catch (error) {
      console.error("댓글 작성 오류:", error); // 서버 콘솔에 자세한 에러 출력
      res.status(500).json({
        message: "댓글 작성에 실패했습니다.",
        error: error.message, // 클라이언트에 에러 메시지 전달
      });
    }
  },

  // 댓글 수정
  updateComment: async (req, res) => {
    const { content } = req.body;
    const { commentId } = req.params;
    const user_id = req.user.id; // 토큰에서 추출된 사용자 ID

    try {
      console.log("현재 사용자 ID:", user_id); // 디버깅용 로그 추가

      // 댓글 작성자 확인
      const comment = await pool.query(
        "SELECT * FROM comments WHERE comment_id = $1",
        [commentId]
      );

      console.log("댓글 정보:", comment.rows[0]); // 디버깅용 로그 추가

      if (comment.rows.length === 0) {
        return res.status(404).json({ message: "댓글을 찾을 수 없습니다." });
      }

      if (comment.rows[0].user_id !== user_id) {
        console.log("댓글 작성자 ID:", comment.rows[0].user_id); // 디버깅용 로그 추가
        return res
          .status(403)
          .json({ message: "댓글을 수정할 권한이 없습니다." });
      }

      await pool.query(
        "UPDATE comments SET content = $1 WHERE comment_id = $2",
        [content, commentId]
      );

      res.json({ message: "댓글이 수정되었습니다." });
    } catch (error) {
      console.error("댓글 수정 오류:", error);
      res.status(500).json({ message: "댓글 수정에 실패했습니다." });
    }
  },

  // 댓글 삭제
  deleteComment: async (req, res) => {
    const { commentId } = req.params;
    const user_id = req.user.id;

    try {
      console.log("토큰의 user_id:", user_id);

      const comment = await pool.query(
        "SELECT * FROM comments WHERE comment_id = $1",
        [commentId]
      );

      console.log("댓글 정보:", comment.rows[0]);

      if (comment.rows.length === 0) {
        return res.status(404).json({ message: "댓글을 찾을 수 없습니다." });
      }

      if (parseInt(comment.rows[0].user_id) !== parseInt(user_id)) {
        console.log("댓글 작성자 ID:", comment.rows[0].user_id);
        return res
          .status(403)
          .json({ message: "댓글을 삭제할 권한이 없습니다." });
      }

      await pool.query("DELETE FROM comments WHERE comment_id = $1", [
        commentId,
      ]);
      res.json({ message: "댓글이 삭제되었습니다." });
    } catch (error) {
      console.error("댓글 삭제 오류:", error);
      res.status(500).json({
        message: "댓글 삭제에 실패했습니다.",
        error: error.message,
        tokenUserId: user_id,
      });
    }
  },

  // 현재 사용자의 댓글 목록 조회
  getMyComments: async (req, res) => {
    const user_id = req.user.id;

    try {
      const comments = await pool.query(
        `SELECT c.*, w.title as post_title 
             FROM comments c 
             JOIN write w ON c.post_id = w.post_id 
             WHERE c.user_id = $1 
             ORDER BY c.created_at DESC`,
        [user_id]
      );

      res.json(comments.rows);
    } catch (error) {
      console.error("내 댓글 조회 오류:", error);
      res.status(500).json({ message: "댓글 목록을 불러오는데 실패했습니다." });
    }
  },
};

module.exports = commentsController;
