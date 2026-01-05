#ifndef HTTP_RESPONSE_PROCESSOR_H
#define HTTP_RESPONSE_PROCESSOR_H

#include "IHttpResponseProcessor.h"
#include "IHttpResponseQueue.h"
#include <ServerProvider.h>
#include <IHttpResponse.h>
#include <iostream>

/// @Component
class HttpResponseProcessor final : public IHttpResponseProcessor {

    /// @Autowired
    Private IHttpResponseQueuePtr responseQueue;

    Private IServerPtr server;

    Public HttpResponseProcessor() 
        : server(ServerProvider::GetDefaultServer()) {
    }
    
    Public ~HttpResponseProcessor() override = default;

    // ============================================================================
    // HTTP Response Processing Operations
    // ============================================================================
    
    Public Bool ProcessResponse() override {
        std::cout << "[HttpResponseProcessor] ProcessResponse() called" << std::endl;
        
        if (responseQueue->IsEmpty()) {
            std::cout << "[HttpResponseProcessor] Response queue is empty" << std::endl;
            return false;
        }
        
        std::cout << "[HttpResponseProcessor] Response queue is not empty, dequeuing..." << std::endl;
        IHttpResponsePtr response = responseQueue->DequeueResponse();
        if (response == nullptr) {
            std::cout << "[HttpResponseProcessor] ERROR: Dequeued response is nullptr" << std::endl;
            return false;
        }
        
        std::cout << "[HttpResponseProcessor] Successfully dequeued response" << std::endl;
        
        if (server == nullptr) {
            std::cout << "[HttpResponseProcessor] ERROR: Server is nullptr" << std::endl;
            return false;
        }
        
        std::cout << "[HttpResponseProcessor] Server is valid" << std::endl;
        
        // Get request ID from response
        StdString requestId = StdString(response->GetRequestId());
        std::cout << "[HttpResponseProcessor] Request ID from response: '" << requestId << "' (length: " << requestId.length() << ")" << std::endl;
        if (requestId.empty()) {
            std::cout << "[HttpResponseProcessor] ERROR: Request ID is empty!" << std::endl;
            return false;
        }
        
        // Convert response to HTTP string format
        std::cout << "[HttpResponseProcessor] Calling ToHttpString()..." << std::endl;
        StdString responseString = response->ToHttpString();
        std::cout << "[HttpResponseProcessor] ToHttpString() returned length: " << responseString.length() << std::endl;
        if (responseString.empty()) {
            std::cout << "[HttpResponseProcessor] ERROR: Response string is empty!" << std::endl;
            return false;
        }
        
        std::cout << "[HttpResponseProcessor] Response string preview (first 200 chars): " << responseString.substr(0, 200) << std::endl;
        
        // Send response using server
        std::cout << "[HttpResponseProcessor] Calling SendMessage(requestId='" << requestId << "', message length=" << responseString.length() << ")" << std::endl;
        Bool result = server->SendMessage(requestId, responseString);
        std::cout << "[HttpResponseProcessor] SendMessage() returned: " << (result ? "true" : "false") << std::endl;
        return result;
    }
};

#endif // HTTP_RESPONSE_PROCESSOR_H

