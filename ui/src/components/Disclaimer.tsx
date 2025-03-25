import Button from "@mui/material/Button";
import React from "react";
import Modal from "@mui/material/Modal";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "75%",
  bgcolor: "background.paper",
  borderRadius: 2,
  boxShadow: 24,
  p: 4,
  outline: "none",
  "&:focus": {
    outline: "none",
  },
};

export default function Disclaimer({ modalOpen, setModalOpen }) {
  const handleModalClose = () => {
    setModalOpen(false);
  };

  return (
    <div>
      <Modal open={modalOpen} onClose={handleModalClose}>
        <Box sx={style}>
          <Typography
            id="modal-modal-title"
            variant="h6"
            component="h2"
            align="center"
          >
            Disclaimer
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2 }}>
            This application is designed to provide educational information and
            predictive insights regarding diabetes risk based on user-provided
            data. It is not a substitute for professional medical diagnosis,
            advice, or treatment. The diabetes risk assessment and predictions
            provided by this app are based on general information and predictive
            algorithms and do not constitute a formal medical diagnosis.
            Consultation interactions provided through this app with virtual
            professionals (including dieticians, fitness trainers, and
            healthcare professionals) are intended solely for informational and
            educational purposes. They do not replace personalized medical
            advice, diagnosis, or treatment plans provided by qualified
            healthcare providers. Always consult with your healthcare provider
            or physician before making medical decisions or implementing changes
            to your health or fitness routine. If you believe you have symptoms
            indicative of diabetes or any other medical condition, immediately
            seek professional medical attention. Reliance on any information or
            resources provided by this app is at your own risk. The developers,
            creators, and partners associated with this application do not
            assume any liability or responsibility for adverse outcomes or
            damages arising from reliance on the information provided by the
            app, including the predictive results and consultations with virtual
            experts. By using this application, you acknowledge and accept the
            limitations and responsibilities outlined above.
          </Typography>
          <Box sx={{ display: "flex", justifyContent: "center" }}>
            <Button
              variant="contained"
              color="primary"
              sx={{ mt: 4 }}
              onClick={handleModalClose}
            >
              I Acknowledge
            </Button>
          </Box>
        </Box>
      </Modal>
    </div>
  );
}
