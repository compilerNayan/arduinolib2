#ifndef HTTP_RESPONSE_PROCESSOR_H
#define HTTP_RESPONSE_PROCESSOR_H

#include "IHttpResponseProcessor.h"
#include "IHttpResponseQueue.h"
#include <ServerFactory.h>
#include <IHttpResponse.h>
#include <iostream>

/// @Component
class HttpResponseProcessor final : public IHttpResponseProcessor {

    /// @Autowired
    Private IHttpResponseQueuePtr responseQueue;

    Private IServerPtr server;

    Public HttpResponseProcessor() 
        : server(ServerFactory::GetDefaultServer()) {
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
        
        IHttpResponsePtr response = responseQueue->DequeueResponse();
        if (response == nullptr) {
            std::cout << "[HttpResponseProcessor] Dequeued response is nullptr" << std::endl;
            return false;
        }
        
        std::cout << "[HttpResponseProcessor] Processing response with request ID: " << response->GetRequestId() << std::endl;
        
        if (server == nullptr) {
            std::cout << "[HttpResponseProcessor] ERROR: Server is nullptr!" << std::endl;
            return false;
        }
        
        // Get request ID from response
        StdString requestId = StdString(response->GetRequestId());
        if (requestId.empty()) {
            std::cout << "[HttpResponseProcessor] ERROR: Request ID is empty!" << std::endl;
            return false;
        }
        
        // Convert response to HTTP string format
        StdString responseString = response->ToHttpString();
        if (responseString.empty()) {
            std::cout << "[HttpResponseProcessor] ERROR: Response string is empty!" << std::endl;
            return false;
        }
        
        std::cout << "[HttpResponseProcessor] Response string length: " << responseString.length() << std::endl;
        std::cout << "[HttpResponseProcessor] Sending response with request ID: " << requestId << std::endl;
        
        // Send response using server
        Bool result = server->SendMessage(requestId, responseString);
        if (result) {
            std::cout << "[HttpResponseProcessor] Response sent successfully!" << std::endl;
        } else {
            std::cout << "[HttpResponseProcessor] ERROR: Failed to send response!" << std::endl;
        }
        
        return result;
    }
};

#endif // HTTP_RESPONSE_PROCESSOR_H

