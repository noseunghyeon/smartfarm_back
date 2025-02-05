const express = require("express");
const router = express.Router();
const commentsController = require("../controllers/commentsController");
const authController = require("../controllers/authController"); // authController 추가

// 게시글의 모든 댓글 조회
router.get("/:postId", commentsController.getComments);

// 새 댓글 작성 (토큰 검증 미들웨어 추가)
router.post("/", authController.verifyToken, commentsController.createComment);

// 댓글 수정 (토큰 검증 미들웨어 추가)
router.put(
  "/:commentId",
  authController.verifyToken,
  commentsController.updateComment
);

// 댓글 삭제 (토큰 검증 미들웨어 추가)
router.delete(
  "/:commentId",
  authController.verifyToken,
  commentsController.deleteComment
);

// 내 댓글 목록 조회 추가
router.get(
  "/my/comments",
  authController.verifyToken,
  commentsController.getMyComments
);

module.exports = router;
