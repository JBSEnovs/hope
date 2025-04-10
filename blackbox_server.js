const express = require('express');
const axios = require('axios');

class BlackboxAI {
  constructor(model = 'blackboxai') {
    this.apiUrl = 'https://api.blackbox.ai/api/chat';
    this.headers = {
      'Content-Type': 'application/json',
      // Add any necessary headers here, like Authorization if needed
    };
    this.conversationHistory = {}; // Use an object to manage conversation histories by ID
    this.defaultModel = 'blackboxai'; // Default model selection
    /*
    Available model
    gpt-4o
    claude-sonnet-3.5
    gemini-pro
    blackboxai
    */
  }

  async sendMessage(conversationId, content) {
    // Create conversation history if it does not exist
    if (!this.conversationHistory[conversationId]) {
      this.conversationHistory[conversationId] = [];
    }
    
    // First message in the conversation
    const message = { id: conversationId, content, role: 'user' };
    this.conversationHistory[conversationId].push(message);

    const payload = {
      messages: this.conversationHistory[conversationId],
      id: conversationId,
      previewToken: null,
      userId: null,
      codeModelMode: true,
      agentMode: {},
      trendingAgentMode: {},
      isMicMode: false,
      userSystemPrompt: null,
      maxTokens: 1024,
      playgroundTopP: 0.9,
      playgroundTemperature: 0.5,
      isChromeExt: false,
      githubToken: null,
      clickedAnswer2: false,
      clickedAnswer3: false,
      clickedForceWebSearch: false,
      visitFromDelta: false,
      mobileClient: false,
      userSelectedModel: this.model // Dynamic model selection
    };

    try {
      const response = await axios.post(this.apiUrl, payload, { headers: this.headers });
      // Remove unwanted text from response
      const cleanedResponse = response.data.replace(/Generated by BLACKBOX\.AI, try unlimited chat https:\/\/www\.blackbox\.ai\n\n/g, '');
      const assistantMessage = { id: `response-${Date.now()}`, content: cleanedResponse, role: 'assistant' };
      this.conversationHistory[conversationId].push(assistantMessage);
      return assistantMessage.content;
    } catch (error) {
      console.error('Error communicating with Blackbox.ai:', error);
      throw error;
    }
  }

  async continueConversation(conversationId, content) {
    // Check if conversation history exists
    if (!this.conversationHistory[conversationId]) {
      throw new Error('Conversation not found');
    }
    
    // Add user message to conversation history
    const userMessage = { id: conversationId, content, role: 'user' };
    this.conversationHistory[conversationId].push(userMessage);

    const payload = {
      messages: this.conversationHistory[conversationId],
      id: conversationId,
      previewToken: null,
      userId: null,
      codeModelMode: true,
      agentMode: {},
      trendingAgentMode: {},
      isMicMode: false,
      userSystemPrompt: null,
      maxTokens: 1024,
      playgroundTopP: 0.9,
      playgroundTemperature: 0.5,
      isChromeExt: false,
      githubToken: null,
      clickedAnswer2: false,
      clickedAnswer3: false,
      clickedForceWebSearch: false,
      visitFromDelta: false,
      mobileClient: false,
      userSelectedModel: this.model // Dynamic model selection
    };

    try {
      const response = await axios.post(this.apiUrl, payload, { headers: this.headers });
      // Remove unwanted text from response
      const cleanedResponse = response.data.replace(/Generated by BLACKBOX\.AI, try unlimited chat https:\/\/www\.blackbox\.ai\n\n/g, '');
      const assistantMessage = { id: `response-${Date.now()}`, content: cleanedResponse, role: 'assistant' };
      this.conversationHistory[conversationId].push(assistantMessage);
      return assistantMessage.content;
    } catch (error) {
      console.error('Error in continuing conversation with Blackbox.ai:', error);
      throw error;
    }
  }
}

// Create Express app
const app = express();
const port = 3000; // You can change this to any port you prefer

// Initialize BlackboxAI
const blackboxAI = new BlackboxAI();

// Define the API endpoint
app.get('/api/blackbox', async (req, res) => {
  const { text, conversationId, model } = req.query;

  if (!text || !conversationId) {
    return res.status(400).json({ error: 'Text and conversationId are required' });
  }

  if (model) {
    blackboxAI.model = model; // Update model if provided
  }

  try {
    const response = await blackboxAI.sendMessage(conversationId, text);
    res.json({ response });
  } catch (error) {
    res.status(500).json({ error: 'An error occurred while processing your request' });
  }
});

// Define the endpoint for continuing the conversation
app.post('/api/blackbox/continue', express.json(), async (req, res) => {
  const { text, conversationId } = req.body;

  if (!text || !conversationId) {
    return res.status(400).json({ error: 'Text and conversationId are required' });
  }

  try {
    const response = await blackboxAI.continueConversation(conversationId, text);
    res.json({ response });
  } catch (error) {
    res.status(500).json({ error: 'An error occurred while continuing the conversation' });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
}); 