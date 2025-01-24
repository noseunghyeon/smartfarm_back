const router = require("express").Router();
const { emailCtrl } = require("../controllers/emailCtrl");

router.post("/send-email", emailCtrl);

module.exports = router;
