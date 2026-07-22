package sdk

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
)

// BrainClient wraps REST API interaction with the AI Context Operating System
type BrainClient struct {
	BaseURL string
}

func NewBrainClient(baseURL string) *BrainClient {
	return &BrainClient{
		BaseURL: strings.TrimSuffix(baseURL, "/"),
	}
}

// ProjectCreate is the request payload to initialize a project
type ProjectCreate struct {
	Name        string `json:"name"`
	Summary     string `json:"summary"`
	Description string `json:"description"`
}

// CreateProject initializes a project node inside the Brain
func (c *BrainClient) CreateProject(name, summary, description string) (map[string]interface{}, error) {
	payload, err := json.Marshal(ProjectCreate{Name: name, Summary: summary, Description: description})
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(fmt.Sprintf("%s/projects", c.BaseURL), "application/json", bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP error: %s", resp.Status)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}

// GetContext retrieves the compiled standard context package from the Brain
func (c *BrainClient) GetContext(project, userGoal, currentTask string) (map[string]interface{}, error) {
	params := url.Values{}
	params.Add("user_goal", userGoal)
	if currentTask != "" {
		params.Add("current_task", currentTask)
	}

	fullURL := fmt.Sprintf("%s/context/%s?%s", c.BaseURL, project, params.Encode())
	resp, err := http.Get(fullURL)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP error: %s", resp.Status)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return result, nil
}
