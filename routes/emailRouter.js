const express = require("express");
const router = express.Router();
const authController = require("../controllers/authController");

router.post("/send", authController.sendEmail);

module.exports = router;
