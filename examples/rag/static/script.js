// RAG System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const collectionNameInput = document.getElementById('collection-name');
    const createCollectionButton = document.getElementById('create-collection');
    const collectionList = document.getElementById('collection-list');
    const refreshCollectionsButton = document.getElementById('refresh-collections');
    const deleteCollectionButton = document.getElementById('delete-collection');
    const documentCountElement = document.getElementById('document-count');
    
    const urlInput = document.getElementById('url');
    const scrapeCollectionSelect = document.getElementById('scrape-collection');
    const scrapeButton = document.getElementById('scrape-button');
    const scrapeStatus = document.getElementById('scrape-status');
    
    const questionInput = document.getElementById('question');
    const queryCollectionSelect = document.getElementById('query-collection');
    const queryButton = document.getElementById('query-button');
    const answerElement = document.getElementById('answer');
    const sourcesListElement = document.getElementById('sources-list');
    
    // Load collections on page load
    loadCollections();
    
    // Event listeners
    createCollectionButton.addEventListener('click', createCollection);
    refreshCollectionsButton.addEventListener('click', loadCollections);
    deleteCollectionButton.addEventListener('click', deleteCollection);
    collectionList.addEventListener('change', updateCollectionInfo);
    scrapeButton.addEventListener('click', scrapeUrl);
    queryButton.addEventListener('click', queryKnowledgeBase);
    
    // Functions
    async function loadCollections() {
        try {
            const response = await fetch('/api/collections');
            const data = await response.json();
            
            // Clear existing options
            collectionList.innerHTML = '<option value="">Select a collection</option>';
            scrapeCollectionSelect.innerHTML = '<option value="">Select a collection</option>';
            queryCollectionSelect.innerHTML = '<option value="">Select a collection</option>';
            
            // Add collections to selects
            if (data.collections && data.collections.length > 0) {
                data.collections.forEach(collection => {
                    const option = document.createElement('option');
                    option.value = collection.collection_name;
                    option.textContent = collection.collection_name;
                    
                    collectionList.appendChild(option.cloneNode(true));
                    scrapeCollectionSelect.appendChild(option.cloneNode(true));
                    queryCollectionSelect.appendChild(option.cloneNode(true));
                });
            }
            
            // Update collection info
            updateCollectionInfo();
        } catch (error) {
            console.error('Error loading collections:', error);
            alert('Failed to load collections. See console for details.');
        }
    }
    
    async function createCollection() {
        const collectionName = collectionNameInput.value.trim();
        
        if (!collectionName) {
            alert('Please enter a collection name.');
            return;
        }
        
        try {
            const response = await fetch('/api/collections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: collectionName,
                    metadata: {
                        created_by: 'web_interface',
                        description: 'Collection created from web interface',
                    },
                }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }
            
            // Clear input
            collectionNameInput.value = '';
            
            // Reload collections
            loadCollections();
            
            // Show success message
            alert(`Collection "${collectionName}" created successfully.`);
        } catch (error) {
            console.error('Error creating collection:', error);
            alert('Failed to create collection. See console for details.');
        }
    }
    
    async function deleteCollection() {
        const collectionName = collectionList.value;
        
        if (!collectionName) {
            alert('Please select a collection to delete.');
            return;
        }
        
        if (!confirm(`Are you sure you want to delete the collection "${collectionName}"? This action cannot be undone.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/collections/${collectionName}`, {
                method: 'DELETE',
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }
            
            // Reload collections
            loadCollections();
            
            // Show success message
            alert(`Collection "${collectionName}" deleted successfully.`);
        } catch (error) {
            console.error('Error deleting collection:', error);
            alert('Failed to delete collection. See console for details.');
        }
    }
    
    async function updateCollectionInfo() {
        const collectionName = collectionList.value;
        
        if (!collectionName) {
            documentCountElement.textContent = '0';
            return;
        }
        
        try {
            const response = await fetch(`/api/collections/${collectionName}/count`);
            const data = await response.json();
            
            if (data.error) {
                documentCountElement.textContent = 'Error';
                return;
            }
            
            documentCountElement.textContent = data.count || 0;
        } catch (error) {
            console.error('Error getting collection info:', error);
            documentCountElement.textContent = 'Error';
        }
    }
    
    async function scrapeUrl() {
        const url = urlInput.value.trim();
        const collectionName = scrapeCollectionSelect.value;
        
        if (!url) {
            alert('Please enter a URL.');
            return;
        }
        
        if (!collectionName) {
            alert('Please select a collection.');
            return;
        }
        
        // Show loading status
        scrapeStatus.innerHTML = '<div class="spinner"></div> Scraping and storing content...';
        scrapeStatus.className = 'status-loading';
        
        // Disable button
        scrapeButton.disabled = true;
        
        try {
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    collection_name: collectionName,
                    metadata: {
                        source_type: 'web',
                        scraped_by: 'web_interface',
                    },
                }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                scrapeStatus.textContent = `Error: ${data.error}`;
                scrapeStatus.className = 'status-error';
                return;
            }
            
            // Show success message
            scrapeStatus.textContent = `Successfully scraped and stored content from ${url}`;
            scrapeStatus.className = 'status-success';
            
            // Update collection info
            updateCollectionInfo();
        } catch (error) {
            console.error('Error scraping URL:', error);
            scrapeStatus.textContent = 'Failed to scrape URL. See console for details.';
            scrapeStatus.className = 'status-error';
        } finally {
            // Enable button
            scrapeButton.disabled = false;
        }
    }
    
    async function queryKnowledgeBase() {
        const question = questionInput.value.trim();
        const collectionName = queryCollectionSelect.value;
        
        if (!question) {
            alert('Please enter a question.');
            return;
        }
        
        if (!collectionName) {
            alert('Please select a collection.');
            return;
        }
        
        // Show loading status
        answerElement.innerHTML = '<div class="spinner"></div> Generating answer...';
        sourcesListElement.innerHTML = '<p class="text-muted">Loading sources...</p>';
        
        // Disable button
        queryButton.disabled = true;
        
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    collection_name: collectionName,
                    limit: 5,
                }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                answerElement.textContent = `Error: ${data.error}`;
                sourcesListElement.innerHTML = '<p class="text-muted">No sources available.</p>';
                return;
            }
            
            // Display answer
            answerElement.textContent = data.answer || 'No answer generated.';
            
            // Display sources
            if (data.search_results && data.search_results.length > 0) {
                sourcesListElement.innerHTML = '';
                
                data.search_results.forEach((result, index) => {
                    const sourceItem = document.createElement('div');
                    sourceItem.className = 'source-item';
                    
                    const sourceContent = document.createElement('p');
                    sourceContent.textContent = result.document.length > 200 
                        ? result.document.substring(0, 200) + '...' 
                        : result.document;
                    
                    const sourceMetadata = document.createElement('p');
                    sourceMetadata.className = 'source-url';
                    
                    if (result.metadata && result.metadata.source) {
                        sourceMetadata.textContent = `Source: ${result.metadata.source}`;
                    } else {
                        sourceMetadata.textContent = `Source ${index + 1}`;
                    }
                    
                    const sourceSimilarity = document.createElement('p');
                    sourceSimilarity.className = 'source-similarity';
                    sourceSimilarity.textContent = `Similarity: ${(result.similarity * 100).toFixed(2)}%`;
                    
                    sourceItem.appendChild(sourceContent);
                    sourceItem.appendChild(sourceMetadata);
                    sourceItem.appendChild(sourceSimilarity);
                    
                    sourcesListElement.appendChild(sourceItem);
                });
            } else {
                sourcesListElement.innerHTML = '<p class="text-muted">No sources available.</p>';
            }
        } catch (error) {
            console.error('Error querying knowledge base:', error);
            answerElement.textContent = 'Failed to query knowledge base. See console for details.';
            sourcesListElement.innerHTML = '<p class="text-muted">No sources available.</p>';
        } finally {
            // Enable button
            queryButton.disabled = false;
        }
    }
});
