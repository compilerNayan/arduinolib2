#ifndef HTTP_REQUEST_MANAGER_H
#define HTTP_REQUEST_MANAGER_H

#include "IHttpRequestManager.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestProcessor.h"
#include <ServerFactory.h>

COMPONENT
class HttpRequestManager final : public IHttpRequestManager {

    AUTOWIRED
    Private IHttpRequestQueuePtr requestQueue;

    AUTOWIRED
    Private IHttpRequestProcessorPtr requestProcessor;

    Private IServerPtr server;

    Public HttpRequestManager() 
        : server(ServerFactory::GetDefaultServer()) {
    }
    
    Public ~HttpRequestManager() override = default;

    // ============================================================================
    // HTTP Request Management Operations
    // ============================================================================
    
    Public Bool RetrieveRequest() override {
        if(server == nullptr) {
            server->Start(8080);
        }

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
        if (requestProcessor == nullptr) {
            return false;
        }
        
        Bool processedAny = false;
        while (requestQueue->HasRequests()) {
            if (requestProcessor->ProcessRequest()) {
                processedAny = true;
            } else {
                break;
            }
        }
        
        return processedAny;
    }
};

#endif // HTTP_REQUEST_MANAGER_H

