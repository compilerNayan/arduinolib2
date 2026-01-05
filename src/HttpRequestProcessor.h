#ifndef HTTP_REQUEST_PROCESSOR_H
#define HTTP_REQUEST_PROCESSOR_H

#include "IHttpRequestProcessor.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestDispatcher.h"
#include "IHttpResponseQueue.h"
#include <IHttpResponse.h>
#include <iostream>

/// @Component
class HttpRequestProcessor final : public IHttpRequestProcessor {

    /// @Autowired
    Private IHttpRequestQueuePtr requestQueue;

    /// @Autowired
    Private IHttpRequestDispatcherPtr dispatcher;

    /// @Autowired
    Private IHttpResponseQueuePtr responseQueue;

    Public HttpRequestProcessor() = default;
    
    Public ~HttpRequestProcessor() override = default;

    // ============================================================================
    // HTTP Request Processing Operations
    // ============================================================================
    
    Public Bool ProcessRequest() override {
        std::cout << "[HttpRequestProcessor] ProcessRequest() called" << std::endl;
        
        if (requestQueue->IsEmpty()) {
            std::cout << "[HttpRequestProcessor] Request queue is empty" << std::endl;
            return false;
        }
        
        IHttpRequestPtr request = requestQueue->DequeueRequest();
        if (request == nullptr) {
            std::cout << "[HttpRequestProcessor] Dequeued request is nullptr" << std::endl;
            return false;
        }
        
        std::cout << "[HttpRequestProcessor] Processing request with ID: " << request->GetRequestId() << std::endl;
        
        // Dispatch request to get response body
        StdString responseBody = dispatcher->DispatchRequest(request);
        std::cout << "[HttpRequestProcessor] DispatchRequest returned body length: " << responseBody.length() << std::endl;
        
        // Get request ID from the request
        StdString requestId = StdString(request->GetRequestId());
        if (requestId.empty()) {
            std::cout << "[HttpRequestProcessor] ERROR: Request ID is empty!" << std::endl;
            return false;
        }
        
        // Create HTTP response with request ID and response body
        IHttpResponsePtr response = IHttpResponse::GetResponse(requestId, responseBody);
        if (response == nullptr) {
            std::cout << "[HttpRequestProcessor] ERROR: Failed to create response!" << std::endl;
            return false;
        }
        
        std::cout << "[HttpRequestProcessor] Created response with request ID: " << response->GetRequestId() << std::endl;
        
        // Enqueue response into response queue
        responseQueue->EnqueueResponse(response);
        std::cout << "[HttpRequestProcessor] Response enqueued successfully" << std::endl;
        
        return true;
    }
};

#endif // HTTP_REQUEST_PROCESSOR_H

