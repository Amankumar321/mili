import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import HTMLtoDOCX from 'html-to-docx';
import juice from 'juice';

const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));

// Health check endpoint
app.get('/', (req, res) => {
  res.send('HTML to DOCX Converter API is running');
});

// DOCX generation endpoint
app.post('/generate-docx', async (req, res) => {
  try {
    const {
      content_html,
      header_html = '',
      footer_html = '',
      watermark_html = '',
      watermark_width = 200,
      watermark_height = 100,
      watermark_rotation = -45,
      watermark_opacity = 0.2,
      footer_last_page_only = false
    } = req.body;

    if (!content_html) {
      res.status(400).json({ error: 'content_html is required' });
      return;
    }

    // Combine watermark with content if provided
    const finalContent = juice(content_html);

    // Handle conditional footer
    const finalFooter = juice(footer_html);

    // Generate DOCX
    const buffer = await HTMLtoDOCX(
      finalContent,
      juice(header_html),
      {
        orientation: "portrait",
        footer: !!footer_html,
        //@ts-ignore
        header: true,
      },
      finalFooter
    );

    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    res.setHeader('Content-Disposition', 'attachment; filename=document.docx');
    res.send(buffer);
    
  } catch (error) {
    console.error('Error generating DOCX:', error);
    res.status(500).json({ error: 'Failed to generate document' });
  }
});

app.get('/test-docx', async (req, res) => {
  try {
    const content = `
      <p>This is a simple test document generated from hardcoded HTML</p>
    `;

    const header = `
      <h1>
        ACME Corporation - Confidential
      </h1>
    `;

    const footer = `
      <div style="text-align: center; font-size: 10px; color: #666;">
        Page {page_number} | Generated on ${new Date().toLocaleDateString()}
      </div>
    `;

    // Generate DOCX
    const buffer = await HTMLtoDOCX(
      content,
      header,
      { 
        orientation: "portrait",
        footer: true,
        //@ts-ignore
        header:true,
      },
      footer
    );

    // Send the file
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    res.setHeader('Content-Disposition', 'attachment; filename=test-document.docx');
    res.send(buffer);

  } catch (error) {
    console.error('Test generation failed:', error);
    res.status(500).send('Document generation failed');
  }
});


// Start server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});