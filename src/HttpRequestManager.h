#ifndef HTTP_REQUEST_MANAGER_H
#define HTTP_REQUEST_MANAGER_H

#include "IHttpRequestManager.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestProcessor.h"
#include "IHttpResponseProcessor.h"
#include <ServerFactory.h>
#include <iostream>

/// @Component
class HttpRequestManager final : public IHttpRequestManager {

    /// @Autowired
    Private IHttpRequestQueuePtr requestQueue;

    /// @Autowired
    Private IHttpRequestProcessorPtr requestProcessor;

    /// @Autowired
    Private IHttpResponseProcessorPtr responseProcessor;

    Private IServerPtr server;

    Public HttpRequestManager() 
        : server(ServerFactory::GetDefaultServer()) {
            server->Start(8080);
    }
    
    Public ~HttpRequestManager() override = default;

    // ============================================================================
    // HTTP Request Management Operations
    // ============================================================================
    
    Public Bool RetrieveRequest() override {
        if (server == nullptr) {
            return false;
        }
        
        IHttpRequestPtr request = server->ReceiveMessage();
        if (request == nullptr) {
            return false;
        }
        
        requestQueue->EnqueueRequest(request);
        return true;
    }
    
    Public Bool ProcessRequest() override {
        std::cout << "[HttpRequestManager] ProcessRequest() called" << std::endl;
        
        if (requestProcessor == nullptr) {
            std::cout << "[HttpRequestManager] ERROR: requestProcessor is nullptr!" << std::endl;
            return false;
        }
        
        Bool processedAny = false;
        while (requestQueue->HasRequests()) {
            std::cout << "[HttpRequestManager] Processing request from queue..." << std::endl;
            if (requestProcessor->ProcessRequest()) {
                processedAny = true;
            } else {
                std::cout << "[HttpRequestManager] Request processor returned false, breaking" << std::endl;
                break;
            }
        }
        
        std::cout << "[HttpRequestManager] ProcessRequest() completed. Processed: " << (processedAny ? "true" : "false") << std::endl;
        return processedAny;
    }
    
    Public Bool ProcessResponse() override {
        std::cout << "[HttpRequestManager] ProcessResponse() called" << std::endl;
        
        if (responseProcessor == nullptr) {
            std::cout << "[HttpRequestManager] ERROR: responseProcessor is nullptr!" << std::endl;
            return false;
        }
        
        Bool processedAny = false;
        // Process responses until queue is empty or processor returns false
        while (true) {
            std::cout << "[HttpRequestManager] Processing response from queue..." << std::endl;
            if (responseProcessor->ProcessResponse()) {
                processedAny = true;
            } else {
                std::cout << "[HttpRequestManager] Response processor returned false, breaking" << std::endl;
                break;
            }
        }
        
        std::cout << "[HttpRequestManager] ProcessResponse() completed. Processed: " << (processedAny ? "true" : "false") << std::endl;
        return processedAny;
    }
};

#endif // HTTP_REQUEST_MANAGER_H

