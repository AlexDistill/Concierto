# Content Ingestion Pipeline

## Overview
Automated system for continuously learning from curated sources and building a knowledge base that improves agent performance.

## Architecture

### 1. Source Connectors

```python
# Base connector class
class ContentSource:
    def __init__(self, config):
        self.name = config['name']
        self.type = config['type']
        self.frequency = config['frequency']
        self.last_fetch = None
    
    def fetch(self):
        raise NotImplementedError
    
    def parse(self, raw_content):
        raise NotImplementedError

# Twitter/X Connector
class TwitterSource(ContentSource):
    def __init__(self, config):
        super().__init__(config)
        self.accounts = config['accounts']
        self.api_client = TwitterAPI(config['credentials'])
    
    def fetch(self):
        tweets = []
        for account in self.accounts:
            tweets.extend(self.api_client.get_tweets(
                account, 
                since=self.last_fetch
            ))
        self.last_fetch = datetime.now()
        return tweets
    
    def parse(self, tweets):
        return [{
            'id': tweet.id,
            'text': tweet.text,
            'media': tweet.media_urls,
            'engagement': tweet.metrics,
            'timestamp': tweet.created_at,
            'insights': self.extract_insights(tweet)
        } for tweet in tweets]

# Website Scraper
class WebsiteSource(ContentSource):
    def __init__(self, config):
        super().__init__(config)
        self.url = config['url']
        self.selectors = config['selectors']
    
    def fetch(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        content = {}
        for key, selector in self.selectors.items():
            content[key] = soup.select(selector)
        
        return content
    
    def parse(self, content):
        parsed = []
        for item in content.get('items', []):
            parsed.append({
                'title': item.select_one('.title').text,
                'image': item.select_one('img')['src'],
                'tags': [tag.text for tag in item.select('.tag')],
                'url': item.select_one('a')['href'],
                'extracted': self.extract_design_patterns(item)
            })
        return parsed

# Image Database Connector
class ImageDatabaseSource(ContentSource):
    def __init__(self, config):
        super().__init__(config)
        self.path = config['path']
        self.metadata_path = config.get('metadata_path')
    
    def fetch(self):
        images = []
        for filepath in glob.glob(f"{self.path}/**/*", recursive=True):
            if self.is_image(filepath):
                images.append({
                    'path': filepath,
                    'metadata': self.load_metadata(filepath)
                })
        return images
    
    def parse(self, images):
        return [{
            'id': hashlib.md5(img['path'].encode()).hexdigest(),
            'path': img['path'],
            'type': self.get_image_type(img['path']),
            'dimensions': self.get_dimensions(img['path']),
            'colors': self.extract_colors(img['path']),
            'tags': img['metadata'].get('tags', []),
            'category': img['metadata'].get('category'),
            'usage_rights': img['metadata'].get('rights')
        } for img in images]
```

### 2. Content Processors

```python
class ContentProcessor:
    def __init__(self):
        self.analyzers = {
            'design': DesignAnalyzer(),
            'copy': CopyAnalyzer(),
            'trend': TrendAnalyzer(),
            'sentiment': SentimentAnalyzer()
        }
    
    def process(self, content, content_type):
        results = {}
        
        # Run appropriate analyzers
        if content_type in ['image', 'website']:
            results['design'] = self.analyzers['design'].analyze(content)
        
        if content_type in ['text', 'tweet']:
            results['copy'] = self.analyzers['copy'].analyze(content)
            results['sentiment'] = self.analyzers['sentiment'].analyze(content)
        
        # Always run trend analysis
        results['trend'] = self.analyzers['trend'].analyze(content)
        
        return results

class DesignAnalyzer:
    def analyze(self, content):
        return {
            'colors': self.extract_color_palette(content),
            'typography': self.analyze_typography(content),
            'layout': self.analyze_layout(content),
            'style': self.classify_style(content),
            'trends': self.identify_trends(content)
        }

class TrendAnalyzer:
    def __init__(self):
        self.historical_data = []
    
    def analyze(self, content):
        # Compare with historical data
        emerging = self.identify_emerging_patterns(content)
        declining = self.identify_declining_patterns(content)
        stable = self.identify_stable_patterns(content)
        
        # Update historical data
        self.historical_data.append({
            'timestamp': datetime.now(),
            'patterns': self.extract_patterns(content)
        })
        
        return {
            'emerging': emerging,
            'declining': declining,
            'stable': stable,
            'velocity': self.calculate_trend_velocity(emerging)
        }
```

### 3. Knowledge Base Builder

```python
class KnowledgeBase:
    def __init__(self):
        self.vector_store = VectorDatabase()
        self.pattern_library = {}
        self.inspiration_board = []
        self.performance_data = {}
    
    def add_content(self, processed_content):
        # Store in vector database for similarity search
        embedding = self.create_embedding(processed_content)
        self.vector_store.add(embedding, processed_content)
        
        # Extract and store patterns
        patterns = self.extract_patterns(processed_content)
        for pattern in patterns:
            if pattern['type'] not in self.pattern_library:
                self.pattern_library[pattern['type']] = []
            self.pattern_library[pattern['type']].append(pattern)
        
        # Add to inspiration board if high quality
        if processed_content.get('quality_score', 0) > 0.8:
            self.inspiration_board.append({
                'content': processed_content,
                'added': datetime.now(),
                'tags': self.auto_tag(processed_content)
            })
    
    def query(self, query_text, filters=None):
        # Search vector store
        results = self.vector_store.search(query_text, filters)
        
        # Enhance with patterns
        enhanced_results = []
        for result in results:
            related_patterns = self.find_related_patterns(result)
            enhanced_results.append({
                **result,
                'patterns': related_patterns,
                'performance': self.get_performance_data(result)
            })
        
        return enhanced_results
    
    def get_inspiration(self, criteria):
        filtered = []
        for item in self.inspiration_board:
            if self.matches_criteria(item, criteria):
                filtered.append(item)
        
        # Sort by relevance and recency
        return sorted(filtered, key=lambda x: (
            x.get('relevance_score', 0),
            x['added']
        ), reverse=True)
```

### 4. Training Data Generator

```python
class TrainingDataGenerator:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.training_sets = {}
    
    def generate_training_data(self, agent_type):
        # Get relevant content from knowledge base
        relevant_content = self.kb.query(
            f"training data for {agent_type}",
            filters={'high_performance': True}
        )
        
        # Create training examples
        training_data = []
        for content in relevant_content:
            example = self.create_training_example(content, agent_type)
            if example:
                training_data.append(example)
        
        # Augment with variations
        augmented = self.augment_data(training_data)
        
        # Split into train/validation sets
        return self.split_data(augmented)
    
    def create_training_example(self, content, agent_type):
        if agent_type == 'content-creator':
            return {
                'input': content.get('brief', ''),
                'output': content.get('final_content', ''),
                'performance': content.get('engagement_metrics', {}),
                'feedback': content.get('human_feedback', '')
            }
        elif agent_type == 'visual-storyteller':
            return {
                'input': content.get('concept', ''),
                'visuals': content.get('images', []),
                'narrative': content.get('story', ''),
                'impact': content.get('emotional_response', {})
            }
        # Add more agent-specific training examples
```

### 5. Automation Scripts

```yaml
# Ingestion Schedule Configuration
ingestion_schedule:
  sources:
    twitter_figsfromplums:
      type: twitter
      account: "@FigsFromPlums"
      frequency: "every 2 hours"
      processor: trend-researcher
      
    siteinspire:
      type: website
      url: "https://siteinspire.com"
      frequency: "daily at 9am"
      processor: innovation-catalyst
      
    brand_assets:
      type: database
      path: "/content/brand-assets"
      frequency: "on_change"
      processor: brand-guardian

  processing_pipeline:
    1. fetch_new_content
    2. validate_quality
    3. extract_insights
    4. update_knowledge_base
    5. generate_training_data
    6. notify_relevant_agents
    7. trigger_workflows
```

### 6. Integration with Agents

```python
class AgentIntegration:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.agent_subscriptions = {}
    
    def subscribe_agent(self, agent_name, interests):
        self.agent_subscriptions[agent_name] = interests
    
    def notify_agents(self, new_content):
        for agent, interests in self.agent_subscriptions.items():
            if self.matches_interests(new_content, interests):
                self.send_to_agent(agent, new_content)
    
    def send_to_agent(self, agent_name, content):
        # Create agent-specific payload
        payload = self.format_for_agent(agent_name, content)
        
        # Trigger agent workflow
        workflow = WorkflowManager()
        workflow.trigger(agent_name, payload)
    
    def get_inspiration_for_agent(self, agent_name, context):
        # Query knowledge base with agent context
        inspiration = self.kb.get_inspiration({
            'agent': agent_name,
            'context': context,
            'limit': 10
        })
        
        return inspiration
```

## Implementation Roadmap

### Week 1: Basic Infrastructure
- Set up source connectors for Twitter and one website
- Implement basic content processor
- Create simple knowledge base storage

### Week 2: Processing Pipeline
- Add design and trend analyzers
- Implement pattern extraction
- Set up vector database for similarity search

### Week 3: Agent Integration
- Connect pipeline to existing agents
- Set up subscription system
- Create training data generation

### Week 4: Automation
- Implement scheduling system
- Add quality filters
- Create monitoring dashboard

### Week 5: Advanced Features
- Add more content sources
- Implement advanced ML analyzers
- Create feedback loops

### Week 6: Optimization
- Performance tuning
- Add caching layers
- Implement error recovery

## Success Metrics

1. **Content Volume**: 1000+ pieces ingested daily
2. **Processing Speed**: < 5 seconds per item
3. **Relevance Score**: > 80% agent satisfaction
4. **Learning Rate**: 10% improvement in agent performance weekly
5. **Automation Level**: 90% hands-free operation