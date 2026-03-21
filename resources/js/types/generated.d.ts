declare namespace App.Data.Inertia {
    export type InertiaAuthData = {
        user: App.Models.User;
    };
    export type InertiaQuoteData = {
        message: string;
        author: string;
    };
    export type InertiaSharedData = {
        name: string;
        quote: App.Data.Inertia.InertiaQuoteData;
        ziggy: App.Data.Inertia.InertiaZiggyData;
        sidebarOpen: boolean;
        errors: object;
        auth: App.Data.Inertia.InertiaAuthData | null;
    };
    export type InertiaZiggyData = {
        url: string;
        port: number | null;
        defaults: Array<any>;
        routes: Array<any>;
        location: string;
    };
}
declare namespace App.Models {
    export type User = {
        id: number;
        name: string;
        email: string;
        email_verified_at: string | null;
        created_at: string | null;
        updated_at: string | null;
    };
}
