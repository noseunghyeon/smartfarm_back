const router = require("express").Router();
const {
  postAuth,
  postLogin,
  sendEmailVerification,
  findPwd,
  resetPwd,
} = require("../controllers/postAuthCtrl");
const { updateAuth } = require("../controllers/updateAuthCtrl");
const { deleteAuth } = require("../controllers/deleteAuthCtrl");

router.post("/register", postAuth);
router.post("/login", postLogin);
router.post("/emailVerification", sendEmailVerification);
router.put("/update_user/:id", updateAuth);
router.delete("/delete_user/:id", deleteAuth);
router.post("/find_pwd", findPwd);
router.post("/reset_pwd", resetPwd);

module.exports = router;
