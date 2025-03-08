import * as React from "react";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import ReactMarkdown from "react-markdown";
import DOMPurify from "dompurify";
import "../App.css";

function MarkdownRenderer({ content }) {
  if (!content) return null;

  const sanitizedContent = DOMPurify.sanitize(content);

  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => (
          <Typography variant="body2" sx={{ marginBottom: "4px" }} {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol style={{ margin: "0", paddingLeft: "20px" }} {...props} />
        ),
        ul: ({ node, ...props }) => (
          <ul style={{ margin: "0", paddingLeft: "20px" }} {...props} />
        ),
        li: ({ node, ...props }) => (
          <li style={{ marginBottom: "4px" }} {...props} />
        ),
      }}
    >
      {sanitizedContent}
    </ReactMarkdown>
  );
}

export default function Review({ response }) {
  return (
    <div className="reviewContainer">
      <Typography
        sx={{ fontWeight: 400, fontSize: "20px", marginBottom: "16px" }}
        variant="subtitle2"
        gutterBottom
      >
        Recommendations
      </Typography>
      <Grid container>
        {[
          { title: "Endocrinologist", content: response?.endocrinologistRecommendation },
          { title: "Dietician", content: response?.dietitianRecommendation },
          { title: "Fitness Trainer", content: response?.fitnessRecommendation },
          { title: "Overall Recommendation", content: response?.finalRecommendation },
        ].map((item, index) => (
          <React.Fragment key={index}>
            <Stack direction="column" spacing={1} sx={{ width: "100%", mb: 5 }}>
              <Typography
                variant="body1"
                sx={{
                  fontWeight: 400,
                  fontSize: "16px",
                  color: "text.secondary",
                }}
              >
                {item.title}:
              </Typography>
              <MarkdownRenderer content={item.content} />
            </Stack>
          </React.Fragment>
        ))}
      </Grid>
    </div>
  );
}
